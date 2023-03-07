cmake_minimum_required(VERSION 3.0.2)
project(ft_sensor)

## Compile as C++11, supported in ROS Kinetic and newer
# add_compile_options(-std=c++11)
set(CMAKE_CXX_INCLUDE_WHAT_YOU_USE include-what-you-use)

find_package(catkin REQUIRED COMPONENTS roscpp std_msgs roslib)

add_subdirectory(include/lib/U3)
add_subdirectory(include/lib/libATIDAQ)


###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## INCLUDE_DIRS: uncomment this if your package contains header files
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
catkin_package(
#  INCLUDE_DIRS include
 CATKIN_DEPENDS roscpp roslib
#  DEPENDS system_lib
)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations
include_directories(
include
include/lib
${catkin_INCLUDE_DIRS}
${CMAKE_SOURCE_DIR}
)

## Declare a C++ executable
## With catkin_make all packages are built within a single CMake context
## The recommended prefix ensures that target names across packages don't collide
add_executable(readLabjack src/readLabJack.cpp)
add_executable(ftConverter src/ftconverter.cpp)


## Add cmake target dependencies of the executable
## same as for the library above
# add_dependencies(${PROJECT_NAME}_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})
add_dependencies(readLabjack ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})
add_dependencies(ftConverter ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

## Specify libraries to link a library or executable target against
target_link_libraries(readLabjack
  ${catkin_LIBRARIES}
  U3
  labjackusb
)

target_link_libraries(ftConverter
  ${catkin_LIBRARIES}
  ATIDAQ
)
