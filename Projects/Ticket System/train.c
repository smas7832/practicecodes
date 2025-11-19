#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>

/*TODO:
 * -Reimplement time handling using <time.h>
 * -Add Validation for characters
 *
 */

/*--------------Structure Declaration--------------*/

// train schedule
typedef struct schedule {
  bool is_set; // flag for status of schedule
  char departure_station[50];
  float departure_time;
  char arrival_station[50];
  float arrival_time;
} schedule;

// actual train object
typedef struct train {
  int train_ID;
  char train_name[50];
  schedule train_schedule;
} train;

// list of trains (derived from linked list)
typedef struct train_list {
  train *train;
  struct train_list *next_train;
} train_list;

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
    new_train->train_schedule.is_set = false; // default flag to false
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
  new_train->train_schedule.is_set = false; // default flag to false
  new_train->train_name[0] = '\0';          // flag for unset train_name

  return;
}

void print_schedule(schedule curr_schedule) {
  // Validation check
  if (curr_schedule.is_set == false) {
    printf("\nError: Schedule is not set yet.");
    return;
  }
  printf("\n\t--Departure Time and Station:\t%2lf - %s",
         curr_schedule.departure_time, curr_schedule.departure_station);
  printf("\n\t--Arrival Time and Station:\t%2lf - %s",
         curr_schedule.arrival_time, curr_schedule.arrival_station);
}

void add_schedule(train **curr_train) {
  // Validation in case of 'is_set=true' is needed.
  puts("Enter Departure station name:");
  scanf("%49s", (*curr_train)->train_schedule.departure_station);
  puts("Enter Departure Time (HH.mm): ");
  scanf("%f", &(*curr_train)->train_schedule.departure_time);
  puts("Enter arrival station name:");
  scanf("%49s", (*curr_train)->train_schedule.arrival_station);
  puts("Enter Arrival Time (HH.mm): ");
  scanf("%f", &(*curr_train)->train_schedule.arrival_time);
  (*curr_train)->train_schedule.is_set = true;
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
  char train_name[50];
  scanf("%s", (*curr_train)->train_name);
  add_schedule(&(*curr_train));
  puts("\nAdded train info as below:");
  print_train_info(*curr_train);
}

int main(void) {
  train_list *head = NULL;
  create_train(&head);
  add_train_info(&(head->train));
}
