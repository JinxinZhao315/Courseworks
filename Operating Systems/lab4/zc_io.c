#include "zc_io.h"
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <semaphore.h>
#include <fcntl.h>
#include <unistd.h>

// The zc_file struct is analogous to the FILE struct that you get from fopen.
struct zc_file
{
    size_t size;
    size_t offset;
    void *f_ptr;
    int f_des;
    int reader_num;
    sem_t read_mutex;
    sem_t write_mutex;
    sem_t rev_door;
    // Insert the fields you need here.
};

/**************
 * Exercise 1 *
 **************/

zc_file *zc_open(const char *path)
{
    // To implement
    zc_file *zc_f = malloc(sizeof(zc_file));
    zc_f->f_des = open(path, O_CREAT | O_RDWR, S_IRWXU);
    if (zc_f->f_des == -1)
    {
        perror("Open file failed\n");
        free(zc_f);
        return NULL;
    }
    struct stat stat_buff;
    if (fstat(zc_f->f_des, &stat_buff) == -1)
    {
        perror("fstat failed\n");
        free(zc_f);
        return NULL;
    }
    off_t file_size = stat_buff.st_size;
    int mmap_size = file_size == 0 ? 1 : file_size;
    zc_f->f_ptr = mmap(NULL, mmap_size, PROT_WRITE | PROT_READ, MAP_SHARED, zc_f->f_des, 0);
    if (zc_f->f_ptr == MAP_FAILED)
    {
        perror("mmap failed\n");
        free(zc_f);
        return NULL;
    }

    zc_f->offset = 0;
    zc_f->size = mmap_size;
    zc_f->reader_num = 0;

    sem_init(&zc_f->read_mutex, 0, 1);
    sem_init(&zc_f->write_mutex, 0, 1);
    sem_init(&zc_f->rev_door, 0, 1);

    return zc_f;
}

int zc_close(zc_file *file)
{
    // To implement
    int r1 = sem_destroy(&file->read_mutex);
    int r2 = sem_destroy(&file->write_mutex);
    int r3 = sem_destroy(&file->rev_door);
    int unmap_result = munmap(file->f_ptr, file->size);
    int close_result = close(file->f_des);
    free(file);
    return r1 == 0 && r2 == 0 && r3 == 0 && unmap_result == 0 && close_result == 0 ? 0 : -1;
}

const char *zc_read_start(zc_file *file, size_t *size)
{
    // To implement
    sem_wait(&file->rev_door);
    sem_post(&file->rev_door);

    sem_wait(&file->read_mutex);
    file->reader_num += 1;
    if (file->reader_num == 1)
    {
        sem_wait(&file->write_mutex);
    }
    sem_post(&file->read_mutex);

    // Adding a number num to a pointer will return the value of the pointer (address in memory)
    // incremented by num * the_size_of_pointed_type
    char *ret_ptr = (char *)file->f_ptr + file->offset;

    if (file->offset + *size > file->size)
    {
        *size = file->size - file->offset;
        file->offset = file->size;
    }
    else
    {
        file->offset += *size;
    }
    return ret_ptr;
}

void zc_read_end(zc_file *file)
{
    // To implement
    sem_wait(&file->read_mutex);
    file->reader_num -= 1;
    if (file->reader_num == 0)
    {
        sem_post(&file->write_mutex);
    }
    sem_post(&file->read_mutex);
}

/**************
 * Exercise 2 *
 **************/

char *zc_write_start(zc_file *file, size_t size)
{
    // To implement
    sem_wait(&file->rev_door);
    sem_wait(&file->write_mutex);
    size_t new_size = file->offset + size;
    if (new_size > file->size)
    {
        // Increase file size with ftruncate and mremap
        ftruncate(file->f_des, new_size);
        file->f_ptr = mremap(file->f_ptr, file->size, new_size, MREMAP_MAYMOVE);
        file->size = new_size;
        if (file->f_ptr == MAP_FAILED)
        {
            perror("mremap failed\n");
            return NULL;
        }
    }
    char *ret_ptr = (char *)file->f_ptr + file->offset;
    file->offset += size;
    return ret_ptr;
}

void zc_write_end(zc_file *file)
{
    // To implement
    sem_post(&file->write_mutex);
    sem_post(&file->rev_door);
}

/**************
 * Exercise 3 *
 **************/

off_t zc_lseek(zc_file *file, long offset, int whence)
{
    // To implement
    sem_wait(&file->write_mutex);
    long offset_temp = (long)file->offset;
    switch (whence)
    {
    case SEEK_SET:
        offset_temp = offset;
        break;
    case SEEK_CUR:
        offset_temp += offset;
        break;
    case SEEK_END:
        offset_temp = file->size + offset;
        break;
    }
    if (offset_temp < 0 || offset_temp > (long)file->size)
    {
        perror("lseek moves offset out of bound\n");
        sem_post(&file->write_mutex);
        return -1;
    }
    file->offset = offset_temp;
    sem_post(&file->write_mutex);
    return file->offset;
}

/**************
 * Exercise 4 *
 **************/

int zc_copyfile(const char *source, const char *dest)
{
    // To implement
    zc_file *src_f = zc_open(source);
    zc_file *dest_f = zc_open(dest);
    size_t src_size = src_f->size;

    // Change the size of the dest file to be the same as src file
    ftruncate(dest_f->f_des, src_size);
    dest_f->f_ptr = mremap(dest_f->f_ptr, dest_f->size, src_size, MREMAP_MAYMOVE);
    dest_f->size = src_size;
    if (dest_f->f_ptr == MAP_FAILED)
    {
        perror("mremap failed\n");
        return -1;
    }

    ssize_t copy_result = copy_file_range(src_f->f_des, NULL, dest_f->f_des, NULL, src_size, 0);
    if (copy_result == -1)
    {
        perror("Copy file failed\n");
        return -1;
    }
    return 0;
}
