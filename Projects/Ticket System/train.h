#ifndef TRAIN_H
#define TRAIN_H

#include "schedule.h"
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
// maximum length for names (stations, trains)
#define NAME_LEN 50

/*--------------Structure Declarations--------------*/

// The train object structure
typedef struct train {
  int train_ID;
  char train_name[NAME_LEN];
  schedule train_schedule;
} train;

// list of trains (Follows linked list style.)
typedef struct train_list {
  train *train;
  struct train_list *next_train;
} train_list;

/*--------------Function Declarations--------------*/

/**
 * @brief Allocates and initializes a new train node and train object,
 * and adds it to the end of the train list.
 *
 * @param list Pointer to the head of the train_list linked list.
 */
void create_train(train_list **list);

/**
 * @brief Prints the ID, name, and schedule of a given train.
 *
 * @param Pointer to the train object to print.
 */
void print_train_info(train *curr_train);

/**
 * @brief prompts to add train info: ID, name, and schedule.
 *
 * @param pointer to pointer of the train object to update.
 */
void add_train_info(train **curr_train);

#endif // TRAIN_H
