#!/bin/bash
# Seed 30 teachers
BASE_URL="${BASE_URL:-https://schoolmanagement-prod.up.railway.app/api/v1}"
COOKIE_FILE="${COOKIE_FILE:-/tmp/school_seed_cookies.txt}"
SUCCESS=0; FAIL=0

declare -a TEACHERS=(
'{"employee_id":"EMP050","full_name":"Anita Sharma","email":"anita.sharma@school.com","phone":"+91-9800000050","subjects":["Mathematics","Statistics"],"primary_subject":"Mathematics","qualification":"M.Sc. Mathematics","joining_date":"2019-06-01","max_workload_hours":28}'
'{"employee_id":"EMP051","full_name":"Rajesh Menon","email":"rajesh.menon@school.com","phone":"+91-9800000051","subjects":["Physics"],"primary_subject":"Physics","qualification":"M.Sc. Physics","joining_date":"2020-04-15","max_workload_hours":26}'
'{"employee_id":"EMP052","full_name":"Priya Nair","email":"priya.nair@school.com","phone":"+91-9800000052","subjects":["Chemistry","Biology"],"primary_subject":"Chemistry","qualification":"M.Sc. Chemistry","joining_date":"2021-06-01","max_workload_hours":30}'
'{"employee_id":"EMP053","full_name":"Vikram Singh","email":"vikram.singh@school.com","phone":"+91-9800000053","subjects":["English"],"primary_subject":"English","qualification":"M.A. English Literature","joining_date":"2019-08-10","max_workload_hours":28}'
'{"employee_id":"EMP054","full_name":"Deepa Iyer","email":"deepa.iyer@school.com","phone":"+91-9800000054","subjects":["Hindi"],"primary_subject":"Hindi","qualification":"M.A. Hindi","joining_date":"2022-01-15","max_workload_hours":24}'
'{"employee_id":"EMP055","full_name":"Suresh Reddy","email":"suresh.reddy@school.com","phone":"+91-9800000055","subjects":["Computer Science"],"primary_subject":"Computer Science","qualification":"M.Tech Computer Science","joining_date":"2020-07-01","max_workload_hours":26}'
'{"employee_id":"EMP056","full_name":"Kavita Joshi","email":"kavita.joshi@school.com","phone":"+91-9800000056","subjects":["Biology","Chemistry"],"primary_subject":"Biology","qualification":"M.Sc. Botany","joining_date":"2019-06-15","max_workload_hours":28}'
'{"employee_id":"EMP057","full_name":"Mohan Das","email":"mohan.das@school.com","phone":"+91-9800000057","subjects":["Social Studies"],"primary_subject":"Social Studies","qualification":"M.A. History","joining_date":"2021-04-01","max_workload_hours":26}'
'{"employee_id":"EMP058","full_name":"Sunita Patel","email":"sunita.patel@school.com","phone":"+91-9800000058","subjects":["Mathematics"],"primary_subject":"Mathematics","qualification":"M.Sc. Applied Mathematics","joining_date":"2022-06-01","max_workload_hours":30}'
'{"employee_id":"EMP059","full_name":"Arun Kumar","email":"arun.kumar@school.com","phone":"+91-9800000059","subjects":["Physics","Mathematics"],"primary_subject":"Physics","qualification":"M.Sc. Physics, B.Ed.","joining_date":"2020-01-10","max_workload_hours":28}'
'{"employee_id":"EMP060","full_name":"Geeta Rao","email":"geeta.rao@school.com","phone":"+91-9800000060","subjects":["English","Hindi"],"primary_subject":"English","qualification":"M.A. English, B.Ed.","joining_date":"2019-06-01","max_workload_hours":26}'
'{"employee_id":"EMP061","full_name":"Kiran Desai","email":"kiran.desai@school.com","phone":"+91-9800000061","subjects":["Art"],"primary_subject":"Art","qualification":"B.F.A. Fine Arts","joining_date":"2023-04-01","max_workload_hours":24}'
'{"employee_id":"EMP062","full_name":"Ravi Shankar","email":"ravi.shankar@school.com","phone":"+91-9800000062","subjects":["Physical Education"],"primary_subject":"Physical Education","qualification":"B.P.Ed.","joining_date":"2021-08-01","max_workload_hours":32}'
'{"employee_id":"EMP063","full_name":"Nalini Krishnan","email":"nalini.krishnan@school.com","phone":"+91-9800000063","subjects":["Chemistry"],"primary_subject":"Chemistry","qualification":"Ph.D. Chemistry","joining_date":"2019-04-15","max_workload_hours":26}'
'{"employee_id":"EMP064","full_name":"Amit Verma","email":"amit.verma@school.com","phone":"+91-9800000064","subjects":["Mathematics","Computer Science"],"primary_subject":"Mathematics","qualification":"M.Sc. Mathematics, MCA","joining_date":"2020-06-01","max_workload_hours":28}'
'{"employee_id":"EMP065","full_name":"Pooja Gupta","email":"pooja.gupta@school.com","phone":"+91-9800000065","subjects":["Biology"],"primary_subject":"Biology","qualification":"M.Sc. Zoology","joining_date":"2022-07-01","max_workload_hours":26}'
'{"employee_id":"EMP066","full_name":"Sanjay Tiwari","email":"sanjay.tiwari@school.com","phone":"+91-9800000066","subjects":["Social Studies","English"],"primary_subject":"Social Studies","qualification":"M.A. Political Science","joining_date":"2021-01-10","max_workload_hours":28}'
'{"employee_id":"EMP067","full_name":"Meera Pillai","email":"meera.pillai@school.com","phone":"+91-9800000067","subjects":["Hindi"],"primary_subject":"Hindi","qualification":"M.A. Hindi Literature","joining_date":"2023-06-01","max_workload_hours":24}'
'{"employee_id":"EMP068","full_name":"Vivek Chauhan","email":"vivek.chauhan@school.com","phone":"+91-9800000068","subjects":["Physics"],"primary_subject":"Physics","qualification":"M.Sc. Physics, B.Ed.","joining_date":"2020-09-01","max_workload_hours":28}'
'{"employee_id":"EMP069","full_name":"Rekha Bhat","email":"rekha.bhat@school.com","phone":"+91-9800000069","subjects":["English"],"primary_subject":"English","qualification":"M.Phil. English","joining_date":"2019-06-15","max_workload_hours":26}'
'{"employee_id":"EMP070","full_name":"Prasad Kulkarni","email":"prasad.kulkarni@school.com","phone":"+91-9800000070","subjects":["Computer Science","Mathematics"],"primary_subject":"Computer Science","qualification":"M.Tech. IT","joining_date":"2022-04-01","max_workload_hours":30}'
'{"employee_id":"EMP071","full_name":"Shanti Devi","email":"shanti.devi@school.com","phone":"+91-9800000071","subjects":["Social Studies"],"primary_subject":"Social Studies","qualification":"M.A. Geography","joining_date":"2021-06-01","max_workload_hours":26}'
'{"employee_id":"EMP072","full_name":"Harish Babu","email":"harish.babu@school.com","phone":"+91-9800000072","subjects":["Chemistry","Physics"],"primary_subject":"Chemistry","qualification":"M.Sc. Physical Chemistry","joining_date":"2020-03-15","max_workload_hours":28}'
'{"employee_id":"EMP073","full_name":"Latha Subramaniam","email":"latha.subra@school.com","phone":"+91-9800000073","subjects":["Mathematics"],"primary_subject":"Mathematics","qualification":"M.Sc. Mathematics, Ph.D.","joining_date":"2019-01-10","max_workload_hours":26}'
'{"employee_id":"EMP074","full_name":"Nitin Agarwal","email":"nitin.agarwal@school.com","phone":"+91-9800000074","subjects":["Physical Education"],"primary_subject":"Physical Education","qualification":"M.P.Ed.","joining_date":"2023-08-01","max_workload_hours":32}'
'{"employee_id":"EMP075","full_name":"Padma Lakshmi","email":"padma.lakshmi@school.com","phone":"+91-9800000075","subjects":["Biology","Chemistry"],"primary_subject":"Biology","qualification":"M.Sc. Microbiology","joining_date":"2022-06-15","max_workload_hours":28}'
'{"employee_id":"EMP076","full_name":"Raghav Hegde","email":"raghav.hegde@school.com","phone":"+91-9800000076","subjects":["English","Art"],"primary_subject":"English","qualification":"M.A. English, Diploma Fine Arts","joining_date":"2021-04-01","max_workload_hours":26}'
'{"employee_id":"EMP077","full_name":"Uma Maheshwari","email":"uma.maheshwari@school.com","phone":"+91-9800000077","subjects":["Hindi","Social Studies"],"primary_subject":"Hindi","qualification":"M.A. Hindi, B.Ed.","joining_date":"2020-06-01","max_workload_hours":28}'
'{"employee_id":"EMP078","full_name":"Balaji Srinivasan","email":"balaji.srini@school.com","phone":"+91-9800000078","subjects":["Physics","Mathematics"],"primary_subject":"Physics","qualification":"M.Sc. Astrophysics","joining_date":"2019-07-01","max_workload_hours":26}'
'{"employee_id":"EMP079","full_name":"Divya Narayan","email":"divya.narayan@school.com","phone":"+91-9800000079","subjects":["Computer Science"],"primary_subject":"Computer Science","qualification":"M.Tech. AI/ML","joining_date":"2024-01-15","max_workload_hours":28}'
)

for t in "${TEACHERS[@]}"; do
  RESP=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/admin/teachers" \
    -X POST -H 'Content-Type: application/json' -H 'X-School-Code: SCH001' -b "$COOKIE_FILE" \
    --data-raw "$t")
  if [ "$RESP" = "201" ]; then ((SUCCESS++)); else ((FAIL++)); fi
done
echo "Teachers: $SUCCESS created, $FAIL skipped/failed"
