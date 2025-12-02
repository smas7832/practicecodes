#ifndef SCHEDULE_H
#define SCHEDULE_H

#include <stdbool.h>
#include <stdio.h>
#include <strings.h>
#include <time.h>

#define NAME_LEN 50
// train schedule

typedef struct timendate {

} timendate;

typedef enum { SET, UNSET, PARTIAL } schdl_status;
// Schedule for train
typedef struct schedule {
  schdl_status is_set; // flag for status of schedule
  char departure_station[NAME_LEN];
  char arrival_station[NAME_LEN];
  struct tm departure_timendate; // Departure time for
  struct tm arrival_timendate;
} schedule;
/*
 * @brief prints given schedule structure members
 * @param struct schedule
 */
void print_schedule(schedule *const);

/*
 * @brief add data to given train structure pointer
 * @param pointer to pointer to train struture
 */
typedef struct train train;
void add_schedule(train **curr_train);

#endif
