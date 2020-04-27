CC = g++
LD = $(CC)

TARGET = rmqtest

SRC_DIR = ./src
INCLUDE_DIR += ./include

C_FLAGS = -g -Wall -std=c++11
LD_FLAFS = 
LD_LIBS =
INCLUDES = -I$(INCLUDE_DIR)

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
	rm -f *.o
