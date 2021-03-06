#******************************************************************************
#
# Makefile - Rules for building the project example.
#
# Copyright (c) 2013-2015 Texas Instruments Incorporated.  All rights reserved.
# Software License Agreement
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#
#   Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the
#   distribution.
#
#   Neither the name of Texas Instruments Incorporated nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# This is part of revision 2.1.2.111 of the Tiva Firmware Development Package.
#
#******************************************************************************

#
# Defines the part type that this project uses.
#
PART=TM4C123GH6PM

#
# Define target name
#
TARGET_NAME=firmware

SIZE_CMD=arm-none-eabi-size

#
# The base directory for TivaWare.
#
#ROOT=../../../..
#ROOT=D:/Projekty/TivaWare_C_Series-2.1.3.156
#ROOT=D:/Projekty/TivaWare_C_Series-2.1.4.178
ROOT=/home/ondrej/Projekty/__TivaWare__

#
# Include the common make definitions.
#
include ${ROOT}/makedefs

#
# Where to find source files that do not live in this directory.
#
VPATH=${ROOT}
VPATH+=${ROOT}/utils

#
# Where to find header files that do not live in the source directory.
#
IPATH=.
IPATH+=${ROOT}

#
# The default rule, which causes the project example to be built.
#
Release: all
all: ${COMPILER}
all: ${COMPILER}/${TARGET_NAME}.axf
all: sizeof

sizeof:
	${SIZE_CMD} ${COMPILER}/${TARGET_NAME}.axf

#
# The rule to clean out all the build products.
#
cleanRelease: clean
clean:
	@rm -rf ${COMPILER} ${wildcard *~}

#
# The rule to create the target directory.
#
${COMPILER}:
	@mkdir -p ${COMPILER}

#
# Rules for building the project example.
#
${COMPILER}/${TARGET_NAME}.axf: ${COMPILER}/project.o
${COMPILER}/${TARGET_NAME}.axf: ${COMPILER}/timer.o
${COMPILER}/${TARGET_NAME}.axf: ${COMPILER}/startup_${COMPILER}.o
${COMPILER}/${TARGET_NAME}.axf: ${ROOT}/driverlib/${COMPILER}/libdriver.a
${COMPILER}/${TARGET_NAME}.axf: project.ld
SCATTERgcc_${TARGET_NAME}=project.ld
ENTRY_${TARGET_NAME}=ResetISR
CFLAGSgcc=-DTARGET_IS_TM4C123_RA3

#
# Include the automatically generated dependency files.
#
ifneq (${MAKECMDGOALS},clean)
-include ${wildcard ${COMPILER}/*.d} __dummy__
endif

program:
	openocd -f /usr/share/openocd/scripts/board/ek-lm4f120xl.cfg -c "program ./gcc/${TARGET_NAME}.axf verify reset"

program_win:
	openocd -s "C:/Program Files/OpenOCD/scripts" -f board/ek-lm4f120xl.cfg -c "adapter_khz 100" -c "program ./gcc/${TARGET_NAME}.axf verify reset exit"
