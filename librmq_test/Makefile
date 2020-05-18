CC = g++
LD = $(CC)

TARGET = rmqtest

SRC_DIR = ./src
INCLUDE_DIR += ./include

C_FLAGS = -g -O0 -Wall -Wextra -std=c++11
LD_FLAFS = 
LD_LIBS = -lpthread -L./libs -levent_core -lrabbitmq_r -levent_pthreads -lkdvlog -lkprop -losp
INCLUDES = -I$(INCLUDE_DIR) -I$(INCLUDE_DIR)/libevent2 -I$(INCLUDE_DIR)/libevent2/linux

ifeq ($(CC), g++)
	TYPE = cpp
	SRCS += $(wildcard $(SRC_DIR)/*.$(TYPE))
	OBJS += $(patsubst %.$(TYPE), %.o, $(SRCS))
else
	TYPE = c
	SRCS += $(wildcard $(SRC_DIR)/*.$(TYPE))
	OBJS += $(patsubst %.$(TYPE), %.o, $(SRCS))
endif

all : $(TARGET)
	@echo "Builded target:" $^
	@echo "Done"

$(TARGET) : $(OBJS)
	@echo "Linking" $@ "from" $^ "..."
	$(LD) -o $@ $^ $(LD_FLAGS) $(LD_LIBS)
	@echo "Link finished\n"

$(OBJS) : %.o:%.$(TYPE) 
	@echo "Compiling" $@ "from" $< "..."
	$(CC) -c -o $@ $< $(C_FLAGS) $(INCLUDES)
	@echo "Compile finished\n"

.PHONY : clean cleanobj
clean : cleanobj
	@echo "Remove all executable files"
	rm -f $(TARGET)
cleanobj :
	@echo "Remove binary files"
	rm -f $(SRC_DIR)/*.o
