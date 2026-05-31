#!/bin/bash
# Seed transport data: 20 vehicles, 20 drivers, 15 helpers, 15 routes
BASE_URL="${BASE_URL:-https://schoolmanagement-prod.up.railway.app/api/v1}"
COOKIE_FILE="${COOKIE_FILE:-/tmp/school_seed_cookies.txt}"

# === VEHICLES (20) ===
V_SUCCESS=0; V_FAIL=0
declare -a VEHICLES=(
'{"vehicle_number":"BUS-010","plate_number":"KA-01-XX-1010","type":"Bus","model":"Tata Starbus","year":2019,"fuel_type":"Diesel","capacity":50,"status":"Operational","insurance_expiry":"2027-12-31","fitness_expiry":"2026-12-31"}'
'{"vehicle_number":"BUS-011","plate_number":"KA-01-XX-1011","type":"Bus","model":"Ashok Leyland","year":2020,"fuel_type":"Diesel","capacity":48,"status":"Operational","insurance_expiry":"2027-12-31","fitness_expiry":"2026-12-31"}'
'{"vehicle_number":"BUS-012","plate_number":"KA-01-XX-1012","type":"Bus","model":"Eicher Skyline","year":2021,"fuel_type":"Diesel","capacity":45,"status":"Operational","insurance_expiry":"2027-12-31","fitness_expiry":"2026-12-31"}'
'{"vehicle_number":"BUS-013","plate_number":"KA-01-XX-1013","type":"Bus","model":"Tata Starbus","year":2022,"fuel_type":"Diesel","capacity":52,"status":"Operational","insurance_expiry":"2027-12-31","fitness_expiry":"2026-12-31"}'
'{"vehicle_number":"BUS-014","plate_number":"KA-01-XX-1014","type":"Bus","model":"Ashok Leyland","year":2023,"fuel_type":"Diesel","capacity":50,"status":"Operational","insurance_expiry":"2028-06-30","fitness_expiry":"2027-06-30"}'
'{"vehicle_number":"BUS-015","plate_number":"KA-01-XX-1015","type":"Bus","model":"BharatBenz","year":2024,"fuel_type":"Diesel","capacity":48,"status":"Operational","insurance_expiry":"2028-12-31","fitness_expiry":"2027-12-31"}'
'{"vehicle_number":"BUS-016","plate_number":"KA-01-XX-1016","type":"Bus","model":"Tata LP","year":2020,"fuel_type":"Diesel","capacity":45,"status":"Operational","insurance_expiry":"2027-06-30","fitness_expiry":"2026-06-30"}'
'{"vehicle_number":"BUS-017","plate_number":"KA-01-XX-1017","type":"Bus","model":"Ashok Leyland","year":2021,"fuel_type":"Diesel","capacity":50,"status":"Operational","insurance_expiry":"2027-12-31","fitness_expiry":"2026-12-31"}'
'{"vehicle_number":"BUS-018","plate_number":"KA-01-XX-1018","type":"Bus","model":"Eicher Skyline","year":2022,"fuel_type":"Diesel","capacity":48,"status":"Operational","insurance_expiry":"2028-06-30","fitness_expiry":"2027-06-30"}'
'{"vehicle_number":"BUS-019","plate_number":"KA-01-XX-1019","type":"Bus","model":"Tata Starbus","year":2023,"fuel_type":"Diesel","capacity":55,"status":"Operational","insurance_expiry":"2028-12-31","fitness_expiry":"2027-12-31"}'
'{"vehicle_number":"BUS-020","plate_number":"KA-01-XX-1020","type":"Bus","model":"Ashok Leyland","year":2019,"fuel_type":"Diesel","capacity":50,"status":"Operational","insurance_expiry":"2027-06-30","fitness_expiry":"2026-06-30"}'
'{"vehicle_number":"BUS-021","plate_number":"KA-01-XX-1021","type":"Bus","model":"Tata LP","year":2020,"fuel_type":"Diesel","capacity":48,"status":"Operational","insurance_expiry":"2027-12-31","fitness_expiry":"2026-12-31"}'
'{"vehicle_number":"VAN-010","plate_number":"KA-01-VV-1010","type":"Van","model":"Force Traveller","year":2022,"fuel_type":"Diesel","capacity":12,"status":"Operational","insurance_expiry":"2027-12-31","fitness_expiry":"2026-12-31"}'
'{"vehicle_number":"VAN-011","plate_number":"KA-01-VV-1011","type":"Van","model":"Tata Winger","year":2023,"fuel_type":"Diesel","capacity":14,"status":"Operational","insurance_expiry":"2028-06-30","fitness_expiry":"2027-06-30"}'
'{"vehicle_number":"VAN-012","plate_number":"KA-01-VV-1012","type":"Van","model":"Mahindra Supro","year":2024,"fuel_type":"Diesel","capacity":15,"status":"Operational","insurance_expiry":"2028-12-31","fitness_expiry":"2027-12-31"}'
'{"vehicle_number":"VAN-013","plate_number":"KA-01-VV-1013","type":"Van","model":"Toyota HiAce","year":2021,"fuel_type":"Diesel","capacity":12,"status":"Operational","insurance_expiry":"2027-06-30","fitness_expiry":"2026-06-30"}'
'{"vehicle_number":"VAN-014","plate_number":"KA-01-VV-1014","type":"Van","model":"Tata Winger","year":2022,"fuel_type":"Diesel","capacity":14,"status":"Maintenance","insurance_expiry":"2027-12-31","fitness_expiry":"2026-12-31"}'
'{"vehicle_number":"MINI-010","plate_number":"KA-01-MM-1010","type":"Mini-Bus","model":"Force Traveller","year":2020,"fuel_type":"Diesel","capacity":25,"status":"Maintenance","insurance_expiry":"2027-06-30","fitness_expiry":"2026-06-30"}'
'{"vehicle_number":"MINI-011","plate_number":"KA-01-MM-1011","type":"Mini-Bus","model":"Tata LP","year":2023,"fuel_type":"Diesel","capacity":22,"status":"Maintenance","insurance_expiry":"2028-06-30","fitness_expiry":"2027-06-30"}'
'{"vehicle_number":"MINI-012","plate_number":"KA-01-MM-1012","type":"Mini-Bus","model":"Eicher Skyline","year":2024,"fuel_type":"Diesel","capacity":28,"status":"Out-Of-Order","insurance_expiry":"2028-12-31","fitness_expiry":"2027-12-31"}'
)

for v in "${VEHICLES[@]}"; do
  RESP=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/admin/transport/vehicles" \
    -X POST -H 'Content-Type: application/json' -H 'X-School-Code: SCH001' -b "$COOKIE_FILE" --data-raw "$v")
  if [ "$RESP" = "201" ]; then ((V_SUCCESS++)); else ((V_FAIL++)); fi
done
echo "Vehicles: $V_SUCCESS created, $V_FAIL skipped/failed"

# === DRIVERS (20) ===
D_SUCCESS=0; D_FAIL=0
declare -a DRIVERS=(
'{"full_name":"Ramesh Kumar","phone":"+91-7000000010","license_number":"DL-KA-2024-010","license_type":"Heavy Vehicle","license_expiry":"2028-06-30","experience_years":15,"join_date":"2018-04-01"}'
'{"full_name":"Suresh Yadav","phone":"+91-7000000011","license_number":"DL-KA-2024-011","license_type":"Heavy Vehicle","license_expiry":"2028-06-30","experience_years":12,"join_date":"2019-06-15"}'
'{"full_name":"Mahesh Singh","phone":"+91-7000000012","license_number":"DL-KA-2024-012","license_type":"Heavy Vehicle","license_expiry":"2029-01-15","experience_years":8,"join_date":"2020-01-10"}'
'{"full_name":"Ganesh Reddy","phone":"+91-7000000013","license_number":"DL-KA-2024-013","license_type":"Heavy Vehicle","license_expiry":"2028-12-31","experience_years":20,"join_date":"2017-08-20"}'
'{"full_name":"Dinesh Sharma","phone":"+91-7000000014","license_number":"DL-KA-2024-014","license_type":"Heavy Vehicle","license_expiry":"2029-06-30","experience_years":6,"join_date":"2021-03-01"}'
'{"full_name":"Rajkumar Patel","phone":"+91-7000000015","license_number":"DL-KA-2024-015","license_type":"Heavy Vehicle","license_expiry":"2028-09-15","experience_years":10,"join_date":"2019-11-15"}'
'{"full_name":"Vijay Nair","phone":"+91-7000000016","license_number":"DL-KA-2024-016","license_type":"Heavy Vehicle","license_expiry":"2029-03-31","experience_years":14,"join_date":"2018-07-01"}'
'{"full_name":"Anil Mishra","phone":"+91-7000000017","license_number":"DL-KA-2024-017","license_type":"Heavy Vehicle","license_expiry":"2028-06-30","experience_years":9,"join_date":"2020-09-10"}'
'{"full_name":"Sunil Gupta","phone":"+91-7000000018","license_number":"DL-KA-2024-018","license_type":"Heavy Vehicle","license_expiry":"2029-12-31","experience_years":11,"join_date":"2019-02-20"}'
'{"full_name":"Manoj Verma","phone":"+91-7000000019","license_number":"DL-KA-2024-019","license_type":"Heavy Vehicle","license_expiry":"2028-03-15","experience_years":7,"join_date":"2021-06-01"}'
'{"full_name":"Deepak Joshi","phone":"+91-7000000020","license_number":"DL-KA-2024-020","license_type":"Heavy Vehicle","license_expiry":"2028-06-30","experience_years":18,"join_date":"2017-12-15"}'
'{"full_name":"Ravi Tiwari","phone":"+91-7000000021","license_number":"DL-KA-2024-021","license_type":"Light Vehicle","license_expiry":"2029-06-30","experience_years":5,"join_date":"2022-01-10"}'
'{"full_name":"Sanjay Das","phone":"+91-7000000022","license_number":"DL-KA-2024-022","license_type":"Heavy Vehicle","license_expiry":"2028-09-30","experience_years":13,"join_date":"2018-10-01"}'
'{"full_name":"Prakash Rao","phone":"+91-7000000023","license_number":"DL-KA-2024-023","license_type":"Heavy Vehicle","license_expiry":"2028-12-31","experience_years":16,"join_date":"2017-05-15"}'
'{"full_name":"Mukesh Pandey","phone":"+91-7000000024","license_number":"DL-KA-2024-024","license_type":"Light Vehicle","license_expiry":"2029-03-31","experience_years":4,"join_date":"2023-04-01"}'
'{"full_name":"Kishore Iyer","phone":"+91-7000000025","license_number":"DL-KA-2024-025","license_type":"Heavy Vehicle","license_expiry":"2028-06-30","experience_years":17,"join_date":"2018-01-20"}'
'{"full_name":"Ashok Menon","phone":"+91-7000000026","license_number":"DL-KA-2024-026","license_type":"Light Vehicle","license_expiry":"2029-09-30","experience_years":3,"join_date":"2024-06-01"}'
'{"full_name":"Gopal Shetty","phone":"+91-7000000027","license_number":"DL-KA-2024-027","license_type":"Heavy Vehicle","license_expiry":"2028-12-31","experience_years":19,"join_date":"2017-03-10"}'
'{"full_name":"Naresh Pillai","phone":"+91-7000000028","license_number":"DL-KA-2024-028","license_type":"Heavy Vehicle","license_expiry":"2029-06-30","experience_years":8,"join_date":"2021-08-15"}'
'{"full_name":"Vinod Nambiar","phone":"+91-7000000029","license_number":"DL-KA-2024-029","license_type":"Heavy Vehicle","license_expiry":"2028-09-15","experience_years":12,"join_date":"2019-04-20"}'
)

for d in "${DRIVERS[@]}"; do
  RESP=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/admin/transport/drivers" \
    -X POST -H 'Content-Type: application/json' -H 'X-School-Code: SCH001' -b "$COOKIE_FILE" --data-raw "$d")
  if [ "$RESP" = "201" ]; then ((D_SUCCESS++)); else ((D_FAIL++)); fi
done
echo "Drivers: $D_SUCCESS created, $D_FAIL skipped/failed"

# === HELPERS (15) ===
H_SUCCESS=0; H_FAIL=0
declare -a HELPERS=(
'{"full_name":"Lakshmi Devi","phone":"+91-6000000010","join_date":"2021-04-01"}'
'{"full_name":"Pushpa Singh","phone":"+91-6000000011","join_date":"2022-06-15"}'
'{"full_name":"Sita Ram","phone":"+91-6000000012","join_date":"2020-01-10"}'
'{"full_name":"Kamala Devi","phone":"+91-6000000013","join_date":"2023-08-20"}'
'{"full_name":"Meena Kumari","phone":"+91-6000000014","join_date":"2021-03-01"}'
'{"full_name":"Saroja Bai","phone":"+91-6000000015","join_date":"2022-11-15"}'
'{"full_name":"Radha Krishna","phone":"+91-6000000016","join_date":"2020-07-01"}'
'{"full_name":"Geetha Amma","phone":"+91-6000000017","join_date":"2023-09-10"}'
'{"full_name":"Parvathi Devi","phone":"+91-6000000018","join_date":"2021-02-20"}'
'{"full_name":"Savitri Bai","phone":"+91-6000000019","join_date":"2022-06-01"}'
'{"full_name":"Annapurna Devi","phone":"+91-6000000020","join_date":"2020-12-15"}'
'{"full_name":"Janaki Amma","phone":"+91-6000000021","join_date":"2023-01-10"}'
'{"full_name":"Padma Devi","phone":"+91-6000000022","join_date":"2021-10-01"}'
'{"full_name":"Tulsi Bai","phone":"+91-6000000023","join_date":"2022-05-15"}'
'{"full_name":"Saraswati Devi","phone":"+91-6000000024","join_date":"2023-04-01"}'
)

for h in "${HELPERS[@]}"; do
  RESP=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/admin/transport/helpers" \
    -X POST -H 'Content-Type: application/json' -H 'X-School-Code: SCH001' -b "$COOKIE_FILE" --data-raw "$h")
  if [ "$RESP" = "201" ]; then ((H_SUCCESS++)); else ((H_FAIL++)); fi
done
echo "Helpers: $H_SUCCESS created, $H_FAIL skipped/failed"

# === ROUTES (15) ===
R_SUCCESS=0; R_FAIL=0
declare -a ROUTES=(
'{"name":"Route 10 - Koramangala","area":"South","shift":"Morning","stops":5,"distance_km":18,"start_time":"07:00","end_time":"08:30"}'
'{"name":"Route 11 - Whitefield","area":"East","shift":"Morning","stops":6,"distance_km":25,"start_time":"07:00","end_time":"08:30"}'
'{"name":"Route 12 - Electronic City","area":"South","shift":"Morning","stops":7,"distance_km":30,"start_time":"06:45","end_time":"08:15"}'
'{"name":"Route 13 - Banashankari","area":"South","shift":"Both","stops":4,"distance_km":15,"start_time":"07:15","end_time":"08:15"}'
'{"name":"Route 14 - Yelahanka","area":"North","shift":"Morning","stops":5,"distance_km":22,"start_time":"07:00","end_time":"08:30"}'
'{"name":"Route 15 - Hebbal","area":"North","shift":"Both","stops":6,"distance_km":20,"start_time":"07:00","end_time":"08:15"}'
'{"name":"Route 16 - JP Nagar","area":"South","shift":"Afternoon","stops":4,"distance_km":12,"start_time":"14:30","end_time":"15:30"}'
'{"name":"Route 17 - Marathahalli","area":"East","shift":"Morning","stops":8,"distance_km":28,"start_time":"06:30","end_time":"08:15"}'
'{"name":"Route 18 - HSR Layout","area":"South","shift":"Both","stops":5,"distance_km":16,"start_time":"07:00","end_time":"08:00"}'
'{"name":"Route 19 - Jayanagar","area":"South","shift":"Afternoon","stops":3,"distance_km":10,"start_time":"14:45","end_time":"15:30"}'
'{"name":"Route 20 - Malleshwaram","area":"West","shift":"Morning","stops":6,"distance_km":19,"start_time":"07:00","end_time":"08:15"}'
'{"name":"Route 21 - Rajajinagar","area":"West","shift":"Afternoon","stops":4,"distance_km":14,"start_time":"14:30","end_time":"15:15"}'
'{"name":"Route 22 - BTM Layout","area":"South","shift":"Morning","stops":7,"distance_km":24,"start_time":"06:45","end_time":"08:15"}'
'{"name":"Route 23 - Sarjapur","area":"East","shift":"Both","stops":5,"distance_km":32,"start_time":"06:30","end_time":"08:30"}'
'{"name":"Route 24 - Bellandur","area":"East","shift":"Morning","stops":6,"distance_km":21,"start_time":"07:00","end_time":"08:15"}'
)

for r in "${ROUTES[@]}"; do
  RESP=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/admin/transport/routes" \
    -X POST -H 'Content-Type: application/json' -H 'X-School-Code: SCH001' -b "$COOKIE_FILE" --data-raw "$r")
  if [ "$RESP" = "201" ]; then ((R_SUCCESS++)); else ((R_FAIL++)); fi
done
echo "Routes: $R_SUCCESS created, $R_FAIL skipped/failed"
