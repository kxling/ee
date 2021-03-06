STM32DIR := $(dir $(lastword $(MAKEFILE_LIST)))

define assert_defined
ifeq ($($1),)
$$(error "Please set $1 before including this makefile")
endif
endef

$(eval $(call assert_defined,SRCS))
$(eval $(call assert_defined,PROGRAM_NAME))
$(eval $(call assert_defined,CPU))
$(eval $(call assert_defined,FAMILY))

FAMILY_LOWER := $(shell echo $(FAMILY) | tr A-Z a-z)


OBJS=$(SRCS:.c=.o)

BINDIR := $(HOME)/arm-cross/bin
CC := $(BINDIR)/arm-none-eabi-gcc
LD := $(CC)
OBJCOPY := $(BINDIR)/arm-none-eabi-objcopy
OPENOCD := $(BINDIR)/openocd

CFLAGS := -Wall -Wextra -Wimplicit-function-declaration -Wredundant-decls -Wstrict-prototypes -Wundef -Wshadow -g -fno-common -mcpu=$(CPU) -mthumb -mfloat-abi=hard -MD -D$(FAMILY) -Wfatal-errors -std=c99 -I. -Os

LDFLAGS := --static -lnosys -T $(STM32DIR)/$(FAMILY).ld -nostartfiles -Wl,--gc-sections -mcpu=$(CPU) -mthumb -mfloat-abi=hard -lm -Wl,-Map=$(PROGRAM_NAME).map -lopencm3_$(FAMILY_LOWER)
ifeq ($(FAMILY),STM32F4)
LDFLAGS += -L$(HOME)/arm-cross/arm-none-eabi/lib/fpu
endif

all: $(PROGRAM_NAME).bin

$(SRCS:.c=.o): %.o: %.c $(MAKEFILE_LIST)
	$(CC) -c -o $@ $< $(CFLAGS)

$(PROGRAM_NAME).elf: $(OBJS) $(STM32DIR)/$(FAMILY).ld $(MAKEFILE_LIST)
	$(CC) -o $(PROGRAM_NAME).elf $(OBJS) $(LDFLAGS)

$(PROGRAM_NAME).bin: $(PROGRAM_NAME).elf $(MAKEFILE_LIST)
	$(OBJCOPY) -Obinary $(PROGRAM_NAME).elf $(PROGRAM_NAME).bin

.PHONY: flash dfu
flash: $(PROGRAM_NAME).bin
	$(OPENOCD) -f $(STM32DIR)/$(FAMILY)-openocd.cfg -c "init" -c "reset init" -c "flash write_image erase $(PROGRAM_NAME).bin 0x08000000" -c "reset run" -c "shutdown"

dfu: $(PROGRAM_NAME).bin
	sudo dfu-util --device 0483:df11 --alt 0 -D $< -s 0x08000000
	$(OPENOCD) -f $(STM32DIR)/$(FAMILY)-openocd.cfg -c "init" -c "reset run" -c "shutdown"

clean:
	rm -f *.elf *.bin *.list *.map *.o *.d *~

dbg:
	$(BINDIR)/arm-none-eabi-gdb $(PROGRAM_NAME).elf  -ex "target remote | $(OPENOCD) -f $(STM32DIR)/$(FAMILY)-openocd.cfg -c 'gdb_port pipe'"
