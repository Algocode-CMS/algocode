### BEGIN ejudge auto-generated makefile ###
EJUDGE_PREFIX_DIR ?= /opt/ejudge
EJUDGE_CONTESTS_HOME_DIR ?= /home/judges
EJUDGE_LOCAL_DIR ?= /var/lib/ejudge
EJUDGE_SERVER_BIN_PATH ?= /opt/ejudge/libexec/ejudge/bin

CXX = g++
CXXFLAGS = -Wall -g -O2

PYCHELPER = /home/judges/compile/scripts/python3

EXECUTE = ${EJUDGE_PREFIX_DIR}/bin/ejudge-execute
EXECUTE_FLAGS =  --use-stdin --use-stdout --test-pattern=%02d --corr-pattern=%02d.a --time-limit=2

NORMALIZE = ${EJUDGE_SERVER_BIN_PATH}/ej-normalize
NORMALIZE_FLAGS = --workdir=tests --test-pattern=%02d --corr-pattern=%02d.a

all : main_nlogn_opt solutions/game_mp solutions/main_n2 solutions/validate_second_group solutions/game_ve_slow solutions/main_nlog2n_opt solutions/main_n3 solutions/main_nlogn_opt solutions/validate_first_group solutions/game_mp_bug solutions/validate_third_group solutions/main_nlog2n solutions/main_2n solutions/game_mp_n2 solutions/main_nlogn solutions/game_mp_nlog2n
check_settings : all normalize

main_nlogn_opt : main_nlogn_opt.cpp
	${CXX} -DEJUDGE ${CXXFLAGS} main_nlogn_opt.cpp -omain_nlogn_opt ${CXXLIBS}

answers : main_nlogn_opt
	${EXECUTE} ${EXECUTE_FLAGS} --update-corr --test-dir=tests --workdir=tests --all-tests main_nlogn_opt

answer : main_nlogn_opt
	cd tests && ${EXECUTE} ${EXECUTE_FLAGS} --update-corr --test-num=${TEST_NUM} ../main_nlogn_opt


normalize :
	${NORMALIZE} ${NORMALIZE_FLAGS} --all-tests

solutions/game_mp : solutions/game_mp.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} game_mp.cpp -ogame_mp ${CXXLIBS}
solutions/main_n2 : solutions/main_n2.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} main_n2.cpp -omain_n2 ${CXXLIBS}
solutions/validate_second_group : solutions/validate_second_group.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} validate_second_group.cpp -ovalidate_second_group ${CXXLIBS}
solutions/game_ve_slow : solutions/game_ve_slow.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} game_ve_slow.cpp -ogame_ve_slow ${CXXLIBS}
solutions/main_nlog2n_opt : solutions/main_nlog2n_opt.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} main_nlog2n_opt.cpp -omain_nlog2n_opt ${CXXLIBS}
solutions/main_n3 : solutions/main_n3.py
	cd "solutions" && ${PYCHELPER} main_n3.py main_n3
solutions/main_nlogn_opt : solutions/main_nlogn_opt.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} main_nlogn_opt.cpp -omain_nlogn_opt ${CXXLIBS}
solutions/validate_first_group : solutions/validate_first_group.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} validate_first_group.cpp -ovalidate_first_group ${CXXLIBS}
solutions/game_mp_bug : solutions/game_mp_bug.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} game_mp_bug.cpp -ogame_mp_bug ${CXXLIBS}
solutions/validate_third_group : solutions/validate_third_group.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} validate_third_group.cpp -ovalidate_third_group ${CXXLIBS}
solutions/main_nlog2n : solutions/main_nlog2n.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} main_nlog2n.cpp -omain_nlog2n ${CXXLIBS}
solutions/main_2n : solutions/main_2n.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} main_2n.cpp -omain_2n ${CXXLIBS}
solutions/game_mp_n2 : solutions/game_mp_n2.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} game_mp_n2.cpp -ogame_mp_n2 ${CXXLIBS}
solutions/main_nlogn : solutions/main_nlogn.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} main_nlogn.cpp -omain_nlogn ${CXXLIBS}
solutions/game_mp_nlog2n : solutions/game_mp_nlog2n.cpp
	cd "solutions" && ${CXX} -DEJUDGE ${CXXFLAGS} game_mp_nlog2n.cpp -ogame_mp_nlog2n ${CXXLIBS}
clean :
	-rm -f *.o *.class *.exe *~ *.bak main_nlogn_opt solutions/*.o solutions/game_mp solutions/main_n2 solutions/validate_second_group solutions/game_ve_slow solutions/main_nlog2n_opt solutions/main_n3 solutions/main_nlogn_opt solutions/validate_first_group solutions/game_mp_bug solutions/validate_third_group solutions/main_nlog2n solutions/main_2n solutions/game_mp_n2 solutions/main_nlogn solutions/game_mp_nlog2n

### END ejudge auto-generated makefile ###
