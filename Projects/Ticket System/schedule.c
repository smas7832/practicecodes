#include "schedule.h"
#include "train.h"
#include <stdbool.h>
#include <stdio.h>
#include <strings.h>
#include <time.h>

void get_time() {}

void print_schedule(schedule *curr_schedule) {
  // Validation check
  if (curr_schedule->is_set == UNSET || curr_schedule->is_set == PARTIAL) {
    printf("\nError: Schedule is not set yet.");
    return;
  }
  char buffer[30];
  strftime(buffer, 30, "%x %X", &(curr_schedule->departure_timendate));
  printf("\nDeparture Date and Time:\t");
  puts(buffer);
  printf("\nDeparture Station:\t%s", curr_schedule->departure_station);
  strftime(buffer, 30, "%x %X", &(curr_schedule->arrival_timendate));
  printf("\nArrival Date, Time:\t");
  puts(buffer);
  printf("\nArrival Station:\t%s", curr_schedule->arrival_station);
}

void add_schedule(train **curr_train) {
  // Validation in case of 'is_set=SET' flag is needed.
  puts("Enter Departure station name:");
  scanf("%49s", (*curr_train)->train_schedule.departure_station);
  puts("Enter Arrival station name:");
  scanf("%49s", (*curr_train)->train_schedule.arrival_station);

  int hr, min, mday, month, year;

  puts("Enter Departure Date (dd/mm/yyyy): ");

  do {
    scanf("%d/%d/%d", &mday, &month, &year);
    if (mday > 31 || month > 12 || year < 1900) {
      printf("\nPlease enter Valid Departure Date:");
    }
  } while (mday > 31 || month > 12 || year < 1900);

  puts("Enter Departure Time and Date (HH:mm): ");
  do {
    scanf("%d:%d", &hr, &min);
    if (hr > 23 || min > 59) {
      printf("\nPlease enter Valid Departure Time:");
    }
  } while (hr > 23 || min > 59);

  ((*curr_train)->train_schedule.departure_timendate.tm_hour) = hr;
  ((*curr_train)->train_schedule.departure_timendate.tm_min) = min;
  ((*curr_train)->train_schedule.departure_timendate.tm_mday) = mday;
  ((*curr_train)->train_schedule.departure_timendate.tm_mon) = month;
  ((*curr_train)->train_schedule.departure_timendate.tm_year) = year - 1900;
  ((*curr_train)->train_schedule.departure_timendate.tm_sec) = 00;
  ((*curr_train)->train_schedule.departure_timendate.tm_isdst) = -1;

  puts("Enter Arrival Date (dd/mm/yyyy): ");
  do {
    scanf("%d/%d/%d", &mday, &month, &year);
    if (mday > 31 || month > 12 || year < 1900) {
      printf("\nPlease enter Valid Arrival Date:");
    }
  } while (mday > 31 || month > 12 || year < 1900);

  puts("Enter Arrival Time (HH:mm): ");
  do {
    scanf("%d:%d", &hr, &min);
    if (hr > 23 || min > 59) {
      printf("\nPlease enter Valid Arrival Time:");
    }
  } while (hr > 23 || min > 59);

  ((*curr_train)->train_schedule.arrival_timendate.tm_hour) = hr;
  ((*curr_train)->train_schedule.arrival_timendate.tm_min) = min;
  ((*curr_train)->train_schedule.arrival_timendate.tm_mday) = mday;
  ((*curr_train)->train_schedule.arrival_timendate.tm_mon) = month - 1;
  ((*curr_train)->train_schedule.arrival_timendate.tm_year) = year - 1900;
  ((*curr_train)->train_schedule.arrival_timendate.tm_sec) = 00;
  ((*curr_train)->train_schedule.arrival_timendate.tm_isdst) = -1;

  (*curr_train)->train_schedule.is_set = SET;
}
