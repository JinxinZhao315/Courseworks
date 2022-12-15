/**
 * CS2106 AY22/23 Semester 1 - Lab 2
 *
 * This file contains function definitions. Your implementation should go in
 * this file.
 */

#include "myshell.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <stdbool.h>

struct PCBTable PCB_arr[MAX_PROCESSES];
int free_index = 0;
void sigchld_handler();

void count_process(int option);

void my_init(void)
{
    // Initialize what you need here
}

void sigchld_handler()
{
    int status = -1;
    int exit_code;

    pid_t childPid = waitpid(-1, &status, WNOHANG);

    if (WIFSIGNALED(status))
    {
        exit_code = WTERMSIG(status);
    }
    else if (WIFEXITED(status))
    {
        exit_code = WEXITSTATUS(status);
    }

    for (int i = 0; i < free_index; i++)
    {
        if (PCB_arr[i].pid == childPid)
        {
            PCB_arr[i].status = 1;
            PCB_arr[i].exitCode = exit_code;
            break;
        }
    }
}

void count_process(int option)
{
    int count = 0;
    for (int i = 0; i < free_index; i++)
    {
        if (PCB_arr[i].status == option)
        {
            count += 1;
        }
    }
    char *status_str = option == 1   ? "exited"
                       : option == 2 ? "running"
                       : option == 3 ? "terminating"
                                     : "stopped";

    printf("Total %s process: %d\n", status_str, count);
}

void my_process_command(size_t num_tokens, char **tokens)
{
    // Your code here, refer to the lab document for a description of the
    // arguments
    signal(SIGCHLD, sigchld_handler);
    int prev_counter = -1;
    for (int curr_counter = 0; curr_counter <= (int)num_tokens - 1;
         curr_counter++)
    {
        if (tokens[curr_counter] != NULL && strcmp(tokens[curr_counter], ";") != 0)
        {
            continue;
        }
        else
        {
            int curr_command_size =
                curr_counter - prev_counter; // Including the null terminator
            char *curr_command[curr_command_size];
            for (int i = 0; i < curr_command_size - 1; i++)
            {
                prev_counter += 1;
                curr_command[i] = tokens[prev_counter];
            }
            curr_command[curr_command_size - 1] = NULL;
            prev_counter += 1;

            // Execute current command
            char *command = curr_command[0];

            if (access(command, F_OK) == -1)
            {
                if (strcmp(command, "info") == 0)
                {
                    if (curr_command_size < 3)
                    {
                        fprintf(stderr, "Wrong command\n");
                    }
                    else
                    {
                        int option = atoi(curr_command[1]);
                        if (option == 0)
                        {
                            for (int i = 0; i < free_index; i++)
                            {
                                if (PCB_arr[i].status == 1)
                                {
                                    printf("[%d] %s %d\n",
                                           PCB_arr[i].pid,
                                           "Exited",
                                           PCB_arr[i].exitCode);
                                }
                                else if (PCB_arr[i].status == 2)
                                {
                                    printf("[%d] %s\n",
                                           PCB_arr[i].pid,
                                           "Running");
                                }
                                else if (PCB_arr[i].status == 3)
                                {
                                    printf("[%d] %s\n",
                                           PCB_arr[i].pid,
                                           "Terminating");
                                }
                            }
                        }
                        else if (option == 1 || option == 2 || option == 3 || option == 4)
                        {
                            count_process(option);
                        }
                        else
                        {
                            fprintf(stderr, "Wrong command\n");
                        }
                    }
                }
                else if (strcmp(command, "wait") == 0)
                {
                    if (curr_command_size < 3)
                    {
                        fprintf(stderr, "Wrong command\n");
                    }
                    else
                    {
                        int wait_pid = atoi(curr_command[1]);
                        for (int i = 0; i < free_index; i++)
                        {
                            if (PCB_arr[i].pid == wait_pid)
                            {
                                if (PCB_arr[i].status == 2)
                                {
                                    int status;
                                    waitpid(wait_pid, &status, 0);
                                    if (WIFEXITED(status))
                                    {
                                        int exit_code = WEXITSTATUS(status);
                                        PCB_arr[i].status = 1;
                                        PCB_arr[i].exitCode = exit_code;
                                    }
                                }
                                break;
                            }
                        }
                    }
                }
                else if (strcmp(command, "terminate") == 0)
                {
                    if (curr_command_size < 3)
                    {
                        fprintf(stderr, "Wrong command\n");
                    }
                    else
                    {
                        int term_pid = atoi(curr_command[1]);
                        for (int i = 0; i < free_index; i++)
                        {
                            if (PCB_arr[i].pid == term_pid)
                            {
                                if (PCB_arr[i].status == 2)
                                {
                                    PCB_arr[i].status = 3;
                                    kill(term_pid, SIGTERM);
                                }
                                break;
                            }
                        }
                    }
                }
                else
                {
                    fprintf(stderr, "%s not found\n", command);
                }
            }
            else
            {
                pid_t childPid = fork();
                if (childPid == -1)
                {
                    fprintf(stderr, "Fork failed\n");
                }
                else if (childPid == 0)
                {
                    // Child process

                    // Redirection
                    int in_index = -1, out_index = -1, err_index = -1;
                    bool is_background = false;

                    for (int i = 0; i <= (int)curr_command_size - 2; i++)
                    {
                        if (strcmp(curr_command[i], "<") == 0)
                        {
                            if (i == curr_command_size - 2)
                            { // If "<" is the last non-null token
                                fprintf(stderr, "Wrong command\n");
                                exit(1);
                            }
                            else
                            {
                                in_index = i;
                                int in_file_des = open(curr_command[i + 1], O_RDONLY);
                                if (in_file_des == -1)
                                {
                                    fprintf(stderr, "%s does not exist\n", curr_command[i + 1]);
                                    exit(1);
                                }
                                fflush(stdin);
                                dup2(in_file_des, fileno(stdin));
                                close(in_file_des);
                            }
                        }
                        else if (strcmp(curr_command[i], ">") == 0)
                        {
                            if (i == curr_command_size - 2)
                            {
                                fprintf(stderr, "Wrong command\n");
                                exit(1);
                            }
                            else
                            {
                                out_index = i;
                                int out_file_des = open(curr_command[i + 1], O_WRONLY | O_CREAT | O_TRUNC, 0666);
                                if (out_file_des == -1)
                                {
                                    fprintf(stderr, "Something wrong with opening %s\n", curr_command[i + 1]);
                                    exit(1);
                                }
                                fflush(stdout);
                                dup2(out_file_des, fileno(stdout));
                                close(out_file_des);
                            }
                        }
                        else if (strcmp(curr_command[i], "2>") == 0)
                        {
                            if (i == curr_command_size - 2)
                            {
                                fprintf(stderr, "Wrong command\n");
                                exit(1);
                            }
                            else
                            {
                                err_index = i;
                                int err_file_des = open(curr_command[i + 1], O_WRONLY | O_CREAT | O_TRUNC, 0666);
                                if (err_file_des == -1)
                                {
                                    fprintf(stderr, "Something wrong with opening %s\n", curr_command[i + 1]);
                                    exit(1);
                                }
                                fflush(stderr);
                                dup2(err_file_des, fileno(stderr));
                                close(err_file_des);
                            }
                        }
                        else
                        {
                            // Do nothing
                        }
                    }
                    if (strcmp(curr_command[curr_command_size - 2], "&") == 0)
                    {
                        is_background = true;
                    }

                    int curr_cmd_parsed_size = curr_command_size;
                    if (in_index != -1)
                    {
                        curr_cmd_parsed_size -= 2;
                    }
                    if (out_index != -1)
                    {
                        curr_cmd_parsed_size -= 2;
                    }
                    if (err_index != -1)
                    {
                        curr_cmd_parsed_size -= 2;
                    }
                    if (is_background)
                    {
                        curr_cmd_parsed_size -= 1;
                    }

                    char *curr_cmd_parsed[curr_cmd_parsed_size];
                    int cmd_counter = 0;
                    for (int i = 0; i <= (int)curr_command_size - 2; i++)
                    {
                        if (in_index != -1)
                        {
                            if (i == in_index || i == in_index + 1)
                            {
                                continue;
                            }
                        }
                        if (out_index != -1)
                        {
                            if (i == out_index || i == out_index + 1)
                            {
                                continue;
                            }
                        }
                        if (err_index != -1)
                        {
                            if (i == err_index || i == err_index + 1)
                            {
                                continue;
                            }
                        }
                        if (is_background)
                        {
                            if (i == curr_command_size - 2)
                            {
                                continue;
                            }
                        }
                        curr_cmd_parsed[cmd_counter] = curr_command[i];
                        cmd_counter += 1;
                    }
                    curr_cmd_parsed[cmd_counter] = NULL;
                    // Equality holds: cmd_counter = curr_cmd_noredir_size - 1

                    execvp(command, curr_cmd_parsed);
                }
                else
                {
                    // Parent process
                    struct PCBTable ChildPcb;
                    ChildPcb.pid = childPid;
                    ChildPcb.status = 2;
                    ChildPcb.exitCode = -1;

                    PCB_arr[free_index] = ChildPcb;
                    free_index += 1;

                    if (strcmp(curr_command[curr_command_size - 2], "&") == 0)
                    {
                        printf("Child [%d] in background\n", childPid);
                    }
                    else
                    {

                        int status;

                        waitpid(childPid, &status, 0);

                        if (WIFEXITED(status))
                        {
                            int exit_code = WEXITSTATUS(status);
                            for (int i = 0; i < free_index; i++)
                            {
                                if (PCB_arr[i].pid == childPid)
                                {
                                    PCB_arr[i].status = 1;
                                    PCB_arr[i].exitCode = exit_code;
                                    // printf("Parent: PCBArr[%d]: pid = %d, status = %d, exitcode = %d\n",
                                    //     i, PCB_arr[i].pid, PCB_arr[i].status, PCB_arr[i].exitCode);
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

void my_quit(void)
{
    // Clean up function, called after "quit" is entered as a user command
    for (int i = 0; i < free_index; i++)
    {
        if (PCB_arr[i].status == 2)
        {
            printf("Killing [%d]\n", PCB_arr[i].pid);
            kill(PCB_arr[i].pid, SIGTERM);
        }
    }
    printf("\nGoodbye\n");
}
