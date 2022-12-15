#include <semaphore.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <stddef.h>

#include "packer.h"

typedef struct NODE
{
    int data;
    struct NODE *next;
} node;

typedef struct
{
    node *head;
} queue;

void insert_node_at(queue *lst, int index, int data);
void delete_node_at(queue *lst, int index);
void reset_list(queue *lst);

void insert_node_at(queue *lst, int index, int data)
{

    node *new_node = (node *)malloc(sizeof(node));
    new_node->data = data;
    new_node->next = NULL;

    node *curr = lst->head;

    if (index == 0)
    {
        new_node->next = curr;
        lst->head = new_node;
    }
    else
    {
        for (int i = 1; i <= index - 1; i++)
        {
            curr = curr->next;
        }
        new_node->next = curr->next;
        curr->next = new_node;
    }
}

void delete_node_at(queue *lst, int index)
{

    node *curr = lst->head;

    if (index == 0)
    {
        lst->head = curr->next;
        free(curr);
    }
    else
    {
        for (int i = 1; i <= index - 1; i++)
        {
            curr = curr->next;
        }
        node *node_to_delete = curr->next;
        curr->next = curr->next->next;
        free(node_to_delete);
    }
}

void reset_list(queue *lst)
{

    node *curr = lst->head;
    node *next_node = NULL;

    while (curr != NULL)
    {
        next_node = curr->next;
        free(curr);
        curr = next_node;
    }

    lst->head = NULL;
}

// You can declare global variables here
int N = 2;

sem_t *r_mutex;
sem_t *r_mutex2;
sem_t *r_box_complete;

sem_t *g_mutex;
sem_t *g_mutex2;
sem_t *g_box_complete;

sem_t *b_mutex;
sem_t *b_mutex2;
sem_t *b_box_complete;

queue *red_queue;
queue *green_queue;
queue *blue_queue;
int red_counter = 0;
int green_counter = 0;
int blue_counter = 0;

void packer_init(void)
{
    // Write initialization code here (called once at the start of the program).
    red_queue = (queue *)malloc(sizeof(queue));
    red_queue->head = NULL;
    green_queue = (queue *)malloc(sizeof(queue));
    green_queue->head = NULL;
    blue_queue = (queue *)malloc(sizeof(queue));
    blue_queue->head = NULL;

    r_mutex = malloc(sizeof(sem_t));
    r_mutex2 = malloc(sizeof(sem_t));
    r_box_complete = malloc(sizeof(sem_t));
    sem_init(r_mutex, 0, 1);
    sem_init(r_mutex2, 0, 1);
    sem_init(r_box_complete, 0, 0);

    g_mutex = malloc(sizeof(sem_t));
    g_mutex2 = malloc(sizeof(sem_t));
    g_box_complete = malloc(sizeof(sem_t));
    sem_init(g_mutex, 0, 1);
    sem_init(g_mutex2, 0, 1);
    sem_init(g_box_complete, 0, 0);

    b_mutex = malloc(sizeof(sem_t));
    b_mutex2 = malloc(sizeof(sem_t));
    b_box_complete = malloc(sizeof(sem_t));
    sem_init(b_mutex, 0, 1);
    sem_init(b_mutex2, 0, 1);
    sem_init(b_box_complete, 0, 0);
}

void packer_destroy(void)
{
    // Write deinitialization code here (called once at the end of the program).
    reset_list(red_queue);
    free(red_queue);
    reset_list(green_queue);
    free(green_queue);
    reset_list(blue_queue);
    free(blue_queue);

    sem_destroy(r_mutex);
    free(r_mutex);
    sem_destroy(r_mutex2);
    free(r_mutex2);
    sem_destroy(r_box_complete);
    free(r_box_complete);
    sem_destroy(g_mutex);
    free(g_mutex);
    sem_destroy(g_mutex2);
    free(g_mutex2);
    sem_destroy(g_box_complete);
    free(g_box_complete);

    sem_destroy(b_mutex);
    free(b_mutex);
    sem_destroy(b_mutex2);
    free(b_mutex2);
    sem_destroy(b_box_complete);
    free(b_box_complete);
}

int pack_ball(int colour, int id)
{
    queue *color_queue;
    int *color_counter_ptr;
    sem_t *mutex;
    sem_t *mutex2;
    sem_t *box_complete;
    if (colour == 1)
    {
        color_queue = red_queue;
        color_counter_ptr = &red_counter;
        mutex = r_mutex;
        mutex2 = r_mutex2;
        box_complete = r_box_complete;
    }
    else if (colour == 2)
    {
        color_queue = green_queue;
        color_counter_ptr = &green_counter;
        mutex = g_mutex;
        mutex2 = g_mutex2;
        box_complete = g_box_complete;
    }
    else
    {
        color_queue = blue_queue;
        color_counter_ptr = &blue_counter;
        mutex = b_mutex;
        mutex2 = b_mutex2;
        box_complete = b_box_complete;
    }

    int other_id = -1;
    // bool is_last = false;

    // Rendezvous
    sem_wait(mutex);
    insert_node_at(color_queue, *color_counter_ptr, id);
    *color_counter_ptr += 1;
    if (*color_counter_ptr == N)
    {
        //*color_counter_ptr = 0;
        // is_last = true;
        for (int i = 0; i < N; i++)
        {
            sem_post(box_complete);
        }
    }
    else
    {
        sem_post(mutex);
    }

    sem_wait(box_complete);

    // Critical point

    sem_wait(mutex2);
    *color_counter_ptr -= 1;
    node *curr = color_queue->head;
    // Peek at the other ball's id, do not delete
    for (int i = 0; i < N; i++)
    {
        int data = curr->data;
        if (data != id)
        {

            other_id = data;
        }
        curr = curr->next;
    }
    if (*color_counter_ptr == 0)
    {
        // The last ball pops(deletes) both ball objects from queue
        for (int i = 0; i < N; i++)
        {
            delete_node_at(color_queue, 0);
            // sem_post(turnstile2);
        }
        sem_post(mutex);
    }
    sem_post(mutex2);

    // sem_wait(turnstile2);

    return other_id;
}