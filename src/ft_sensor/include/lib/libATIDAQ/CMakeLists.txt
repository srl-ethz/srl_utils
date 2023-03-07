cmake_minimum_required(VERSION 3.1.0)


set( C_FILES
ftconfig.c
ftrt.c
dom.c
expatls.c
node.c
stack.c
xmlparse.c
xmlrole.c
xmltok.c)

add_library(ATIDAQ ${HEADER_FILES} ${C_FILES})

target_include_directories(ATIDAQ PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
