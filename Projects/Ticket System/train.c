
#include "train.h"
#include "schedule.h"
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#define NAME_LEN 50

/*TODO:
 * -Reimplement time handling using <time.h>
 * -Add Validation for Input data- ONGOING
 *
 */

/*--------------Structure Declaration--------------*/

// The train object

/*--------------Implementation--------------*/

void create_train(train_list **list) {
  // Validation for previous train entries
  if (*list == NULL) {
    // if no previous train:
    //  new space allocated for first train node
    train_list *new_list_train = (train_list *)malloc(sizeof(train_list));
    *list = new_list_train;
    (*list)->next_train = NULL;

    // new actual train object w/ info
    train *new_train = (train *)malloc(sizeof(train));
    (*list)->train = new_train;
    new_train->train_ID = 1001;
    new_train->train_schedule.is_set = UNSET; // default flag to UNSET
    new_train->train_name[0] = '\0';          // flag for unset train_name
    return;
  }
  // if list has old entries:
  train_list *temp_node = *list;
  while (temp_node->next_train != NULL) {
    temp_node = temp_node->next_train;
  }

  // train list
  train_list *new_list_train = (train_list *)malloc(sizeof(train_list));
  temp_node->next_train = new_list_train;
  temp_node->next_train->next_train = NULL;

  // Actual train object
  train *new_train = (train *)malloc(sizeof(train));
  temp_node->train = new_train;
  new_train->train_ID = (temp_node->train->train_ID) + 1;
  new_train->train_schedule.is_set = UNSET; // default flag to false
  new_train->train_name[0] = '\0';          // flag for unset train_name

  return;
}

void print_train_info(train *curr_train) {
  printf("\n\t-----------------\n");
  printf("\nTrain ID:\t%d", (curr_train)->train_ID);
  if (curr_train->train_name[0] == '\0') {
    puts("\nTrain name: is-empty.");
  } else {
    printf("\nTrain name:\t%s", (curr_train)->train_name);
  }
  printf("\nTrain Schedule:\t");
  print_schedule((curr_train)->train_schedule);
  printf("\n\t-----------------\n");
}

void add_train_info(train **curr_train) {
  puts("Already available info of the train:");
  print_train_info(*curr_train);
  printf("\nEnter Train name:");
  char train_name[NAME_LEN];
  scanf("%s", (*curr_train)->train_name);
  add_schedule(&(*curr_train));
  puts("\nAdded train info as below:");
  print_train_info(*curr_train);
}

// int main(void) {
// 	train_list *head = NULL;
// 	create_train(&head);
// 	add_train_info(&(head->train));
// }
