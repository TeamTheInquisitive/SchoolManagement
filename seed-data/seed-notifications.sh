#!/bin/bash
# Seed 30 notifications
BASE_URL="${BASE_URL:-https://schoolmanagement-prod.up.railway.app/api/v1}"
COOKIE_FILE="${COOKIE_FILE:-/tmp/school_seed_cookies.txt}"
SUCCESS=0; FAIL=0

declare -a NOTIFICATIONS=(
'{"title":"Mid-Term Exam Schedule Released","message":"Mid-term examinations will commence from June 10. Please check the detailed schedule on the notice board.","type":"Announcement","target_type":"all","send_via":"in_app"}'
'{"title":"Holiday Notice - Diwali Week","message":"School will remain closed from Oct 28 to Nov 3 on account of Diwali celebrations. Classes resume Nov 4.","type":"Announcement","target_type":"all","send_via":"in_app"}'
'{"title":"Annual Sports Day Registration","message":"Annual Sports Day is on Dec 15. Register for events by Nov 25. Track field and team events available.","type":"Event","target_type":"students","send_via":"in_app"}'
'{"title":"Fee Payment Deadline Reminder","message":"Fee payment for Q3 is due by Nov 15. Late fee of Rs.50/day applicable after grace period.","type":"Reminder","target_type":"parents","send_via":"email"}'
'{"title":"Parent-Teacher Meeting on Dec 5","message":"PTM scheduled for Dec 5 from 9AM to 1PM. All parents requested to attend with student report cards.","type":"Event","target_type":"parents","send_via":"email"}'
'{"title":"Science Exhibition 2026","message":"Inter-house Science Exhibition on Jan 20. Submit project proposals to science teachers by Dec 30.","type":"Event","target_type":"students","send_via":"in_app"}'
'{"title":"New Library Books Available","message":"50 new books added in Science and Literature sections. Visit library to explore and borrow.","type":"Announcement","target_type":"students","send_via":"in_app"}'
'{"title":"Winter Uniform Mandatory from Nov","message":"Winter uniform is mandatory from November 1. Students without proper uniform will not be allowed.","type":"Alert","target_type":"all","send_via":"in_app"}'
'{"title":"Bus Route Change Notice","message":"Route 5 and Route 8 timings changed due to road construction. Check updated timings on portal.","type":"Alert","target_type":"all","send_via":"in_app"}'
'{"title":"Inter-School Quiz Competition","message":"Inter-school quiz competition on Feb 10. Interested students register with class teacher by Jan 25.","type":"Event","target_type":"students","send_via":"in_app"}'
'{"title":"Revised Timetable for Class 10","message":"Revised timetable for Class 10 effective from next Monday. Download from student portal.","type":"Announcement","target_type":"students","send_via":"in_app"}'
'{"title":"Annual Day Rehearsals Begin","message":"Annual Day rehearsals start from Jan 5. Selected students must attend practice after school hours.","type":"Event","target_type":"students","send_via":"in_app"}'
'{"title":"Lab Safety Guidelines Updated","message":"Updated lab safety guidelines are now available. All students must read before next lab session.","type":"Alert","target_type":"students","send_via":"in_app"}'
'{"title":"Scholarship Applications Open","message":"Merit-based scholarships available for academically excellent students. Apply by March 15.","type":"Announcement","target_type":"students","send_via":"in_app"}'
'{"title":"Summer Camp Registration","message":"Summer camp registration is open. Activities include robotics coding art and sports. Limited seats.","type":"Event","target_type":"all","send_via":"in_app"}'
'{"title":"Board Exam Preparation Workshop","message":"Special board exam preparation workshop on weekends starting February. Registration required.","type":"Event","target_type":"students","send_via":"in_app"}'
'{"title":"School Closure - Heavy Rain Alert","message":"Due to heavy rain warning school will remain closed tomorrow. Online classes will be conducted.","type":"Alert","target_type":"all","send_via":"in_app"}'
'{"title":"Cultural Fest Volunteer Signup","message":"Cultural fest needs volunteers for organizing events. Sign up at the student council office.","type":"Event","target_type":"students","send_via":"in_app"}'
'{"title":"Mid-Year Report Cards Ready","message":"Mid-year report cards are ready for collection. Parents can collect from admin office.","type":"Announcement","target_type":"parents","send_via":"email"}'
'{"title":"New Computer Lab Inauguration","message":"New state-of-the-art computer lab inaugurated. Classes will be held in new lab from next week.","type":"Announcement","target_type":"all","send_via":"in_app"}'
'{"title":"Blood Donation Drive - Jan 20","message":"Blood donation drive in collaboration with Red Cross on Jan 20. Eligible students can participate.","type":"Event","target_type":"students","send_via":"in_app"}'
'{"title":"Teacher Training Day - No Classes","message":"Teacher training scheduled for Friday. No regular classes. Self-study assignments will be provided.","type":"Announcement","target_type":"all","send_via":"in_app"}'
'{"title":"Sports Trophy Distribution","message":"Sports trophy distribution ceremony on Saturday at 10AM in school auditorium. All invited.","type":"Event","target_type":"all","send_via":"in_app"}'
'{"title":"Revised Fee Structure Notice","message":"Revised fee structure for academic year 2026-27 is available. Please review on parent portal.","type":"Reminder","target_type":"parents","send_via":"email"}'
'{"title":"Assembly Schedule Change","message":"Morning assembly timing changed to 7:45 AM from next week. Please arrive 10 minutes early.","type":"Announcement","target_type":"all","send_via":"in_app"}'
'{"title":"Guest Lecture - Space Science","message":"Guest lecture on Space Science by ISRO scientist on Feb 28. All science students must attend.","type":"Event","target_type":"students","send_via":"in_app"}'
'{"title":"Extra Classes for Board Students","message":"Extra classes for board exam students starting Jan 15. Schedule available with class teachers.","type":"Announcement","target_type":"students","send_via":"in_app"}'
'{"title":"School Magazine Submissions Open","message":"School magazine accepting submissions - stories poems and artwork. Deadline March 1.","type":"Announcement","target_type":"students","send_via":"in_app"}'
'{"title":"Founders Day Celebration","message":"Founders Day celebration on March 15. Special assembly and cultural programs planned.","type":"Event","target_type":"all","send_via":"in_app"}'
'{"title":"Final Exam Timetable Published","message":"Final exam timetable published. Exams begin April 1. Download from student portal.","type":"Announcement","target_type":"students","send_via":"in_app"}'
)

for n in "${NOTIFICATIONS[@]}"; do
  RESP=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/admin/notifications" \
    -X POST -H 'Content-Type: application/json' -H 'X-School-Code: SCH001' -b "$COOKIE_FILE" --data-raw "$n")
  if [ "$RESP" = "201" ]; then ((SUCCESS++)); else ((FAIL++)); fi
done
echo "Notifications: $SUCCESS created, $FAIL skipped/failed"
