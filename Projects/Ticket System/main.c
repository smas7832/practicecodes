#include "train.h"

train_list *HEAD = NULL;
int main(){
    create_train(&HEAD);
    add_train_info(&(HEAD->train));
    print_train_info((HEAD->train));
}
