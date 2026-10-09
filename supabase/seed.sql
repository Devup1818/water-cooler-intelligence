-- =============================================================================
-- COOL HOME (INDIA) / FRESCO CASA - INITIAL SEED DATA FOR SUPABASE
-- Run this in Supabase SQL Editor after running schema.sql
-- =============================================================================

-- 1. SELLERS (8 Competitors & OEMs)
insert into public.sellers (seller_id, name, seller_type, base_state, gem_seller_id, msme_udyam, notes)
values
  ('D062180000101298', 'Cool Home (India) - Fresco Casa', 'OEM', 'Uttar Pradesh', 'D062180000101298', 'UDYAM-UP-29-0046703', 'Direct OEM manufacturing facility at Hapur, UP. IS 1475 certified, MII Class-1 Local Supplier (>50%), MSME +15% matching preference.'),
  ('VLT-OEM-001', 'Voltas Limited', 'OEM', 'Maharashtra', 'VLT98214', null, 'National HVAC OEM. Primary competitor in Indian Railways (Western/Northern) and MES defence. Win range ₹38.9k-₹39.8k on 150L.'),
  ('BSL-OEM-002', 'Blue Star Limited', 'OEM', 'Maharashtra', 'BSL34019', null, 'Premium national OEM capturing Southern Railway, Central PSUs, and AIIMS. Win range ₹40.5k-₹41.2k on 150L.'),
  ('USH-OEM-003', 'Usha International', 'OEM', 'Delhi', 'USH11029', null, 'Mass consumer manufacturer dominant in 40L and 80L school/tourism tenders at ₹23.5k-₹29.8k.'),
  ('RCE-DLR-001', 'Rajasthan Commercial Enterprises', 'Authorized Dealer', 'Rajasthan', 'RCE88921', null, 'Regional dealer in Jaipur/Jodhpur reselling Blue Star/Voltas at 15-20% markup (₹41.5k). Primary displacement target.'),
  ('SRR-DLR-002', 'Shree Ram Refrigeration Works', 'Authorized Dealer', 'Uttar Pradesh', 'SRR55410', null, 'Western UP local dealer in Meerut and Ghaziabad. Outbids Cool Home on unmonitored municipal tenders at ₹38.5k.'),
  ('WAE-DLR-003', 'Western Aircon & Engineering', 'Authorized Dealer', 'Gujarat', 'WAE66219', null, 'Vadodara/Ahmedabad regional dealer supplying GIDC and state municipalities at ₹41.8k.'),
  ('SCS-DLR-004', 'Southern Cooling Systems', 'Authorized Dealer', 'Tamil Nadu', 'SCS77124', null, 'Chennai dealer capturing TWAD and Greater Chennai Corp at ₹42.4k due to local service response clauses.')
on conflict (seller_id) do update set
  name = excluded.name,
  seller_type = excluded.seller_type,
  notes = excluded.notes;

-- 2. VERIFIED HISTORICAL AWARDS (23 Contracts across India)
insert into public.awards (award_id, source, tender_id, award_date, buyer_org, buyer_state, segment, seller_name, seller_id, seller_type, capacity_class, qty, unit_price, total_value, currency, remarks)
values
  (26, 'gem', 'GEM/2026/B/7789012', '2026-07-08', 'Greater Chennai Corporation', 'Tamil Nadu', 'Municipal', 'Southern Cooling Systems', 'SCS-DLR-004', 'Authorized Dealer', 80, 80.0, 34500.0, 2760000.0, 'INR', 'Chennai primary health centres and schools.'),
  (15, 'gem', 'GEM/2026/B/7654321', '2026-06-15', 'AIIMS Nagpur', 'Maharashtra', 'Health', 'Blue Star Limited', 'BSL-OEM-002', 'OEM', 300, 25.0, 59500.0, 1487500.0, 'INR', 'Hospital OPD high-capacity cold water supply.'),
  (24, 'gem', 'GEM/2026/B/7556789', '2026-06-02', 'Vadodara Municipal Corporation', 'Gujarat', 'Municipal', 'Western Aircon & Engineering', 'WAE-DLR-003', 'Authorized Dealer', 80, 60.0, 33200.0, 1992000.0, 'INR', 'Civic amenities and zonal ward offices.'),
  (22, 'gem', 'GEM/2026/B/7445123', '2026-05-20', 'Ghaziabad Development Authority', 'Uttar Pradesh', 'Urban Dev', 'Shree Ram Refrigeration Works', 'SRR-DLR-002', 'Authorized Dealer', 150, 20.0, 38500.0, 770000.0, 'INR', 'GDA parks and public administrative offices.'),
  (11, 'gem', 'GEM/2026/B/7450123', '2026-05-12', 'Northern Railway (Ambala)', 'Haryana', 'Railways', 'Voltas Limited', 'VLT-OEM-001', 'OEM', 150, 50.0, 39400.0, 1970000.0, 'INR', 'Ambala Division station installations.'),
  (5, 'gem', 'GEM/2026/B/7299831', '2026-04-15', 'Northern Railway (Moradabad)', 'Uttar Pradesh', 'Railways', 'Cool Home (India) - Fresco Casa', 'D062180000101298', 'OEM', 150, 29.0, 35200.0, 1020800.0, 'INR', 'Contract GEMC-511687763924679. Replaced 1550W compressor.'),
  (18, 'gem', 'GEM/2026/B/7345678', '2026-04-02', 'Madhya Pradesh Tourism Development Corp', 'Madhya Pradesh', 'Tourism', 'Usha International', 'USH-OEM-003', 'OEM', 80, 35.0, 29800.0, 1043000.0, 'INR', 'MPTDC highway motels and guest houses.'),
  (14, 'gem', 'GEM/2026/B/7234567', '2026-03-25', 'South Western Railway (Hubballi)', 'Karnataka', 'Railways', 'Blue Star Limited', 'BSL-OEM-002', 'OEM', 150, 65.0, 41200.0, 2678000.0, 'INR', 'Hubballi railway workshop and division.'),
  (4, 'gem', 'GEM/2026/B/7094486', '2026-03-18', 'North Western Railway', 'Rajasthan', 'Railways', 'Cool Home (India) - Fresco Casa', 'D062180000101298', 'OEM', 150, 120.0, 35835.0, 4300200.0, 'INR', 'Awarded Contract GEMC-511687751472352. Strict RITES inspection passed.'),
  (20, 'gem', 'GEM/2026/B/7123999', '2026-02-28', 'Rajasthan State Road Transport Corp (RSRTC)', 'Rajasthan', 'Transport', 'Rajasthan Commercial Enterprises', 'RCE-DLR-001', 'Authorized Dealer', 150, 40.0, 41500.0, 1660000.0, 'INR', 'Bus depot water coolers. Dealer margin captured.'),
  (10, 'gem', 'GEM/2026/B/7112009', '2026-02-18', 'Bharat Heavy Electricals Limited (BHEL)', 'Madhya Pradesh', 'Power/PSU', 'Voltas Limited', 'VLT-OEM-001', 'OEM', 80, 40.0, 31200.0, 1248000.0, 'INR', 'BHEL Bhopal plant staff cafeteria supply.'),
  (13, 'gem', 'GEM/2025/B/6789123', '2025-12-28', 'Gujarat Water Supply & Sewerage Board', 'Gujarat', 'State Dept', 'Blue Star Limited', 'BSL-OEM-002', 'OEM', 80, 70.0, 32400.0, 2268000.0, 'INR', 'GWSSB regional monitoring stations.'),
  (7, 'gem', 'GEM/2025/B/6890123', '2025-12-14', 'North Central Railway (Prayagraj)', 'Uttar Pradesh', 'Railways', 'Cool Home (India) - Fresco Casa', 'D062180000101298', 'OEM', 150, 60.0, 35600.0, 2136000.0, 'INR', 'NCR Station water coolers. Consignee inspection.'),
  (23, 'gem', 'GEM/2025/B/6678123', '2025-12-05', 'Gujarat Industrial Development Corp (GIDC)', 'Gujarat', 'State PSU', 'Western Aircon & Engineering', 'WAE-DLR-003', 'Authorized Dealer', 150, 45.0, 41800.0, 1881000.0, 'INR', 'GIDC Industrial estates Sanand and Dahej.'),
  (6, 'gem', 'GEM/2025/B/6541209', '2025-11-20', 'Urban Development Department UP', 'Uttar Pradesh', 'Municipal', 'Cool Home (India) - Fresco Casa', 'D062180000101298', 'OEM', 80, 45.0, 28400.0, 1278000.0, 'INR', 'Supply of 80L Water Coolers across 12 Nagar Palikas.'),
  (17, 'gem', 'GEM/2025/B/6451230', '2025-11-04', 'Department of School Education UP', 'Uttar Pradesh', 'Education', 'Usha International', 'USH-OEM-003', 'OEM', 40, 95.0, 23800.0, 2261000.0, 'INR', 'Kasturba Gandhi Balika Vidyalayas supply.'),
  (12, 'gem', 'GEM/2025/B/6345678', '2025-10-12', 'Southern Railway (Chennai)', 'Tamil Nadu', 'Railways', 'Blue Star Limited', 'BSL-OEM-002', 'OEM', 150, 110.0, 40500.0, 4455000.0, 'INR', 'Chennai Central & Egmore divisions. RITES cleared.'),
  (19, 'gem', 'GEM/2025/B/6234123', '2025-09-18', 'Public Works Department (PWD) Rajasthan', 'Rajasthan', 'State PWD', 'Rajasthan Commercial Enterprises', 'RCE-DLR-001', 'Authorized Dealer', 80, 50.0, 32900.0, 1645000.0, 'INR', 'Supplied Blue Star units with dealer markup (+15%).'),
  (9, 'gem', 'GEM/2025/B/6123450', '2025-09-05', 'Western Railway (Mumbai)', 'Maharashtra', 'Railways', 'Voltas Limited', 'VLT-OEM-001', 'OEM', 150, 150.0, 38900.0, 5835000.0, 'INR', 'Mumbai Division suburban station coolers.'),
  (21, 'gem', 'GEM/2025/B/6112999', '2025-08-30', 'Nagar Nigam Meerut', 'Uttar Pradesh', 'Municipal', 'Shree Ram Refrigeration Works', 'SRR-DLR-002', 'Authorized Dealer', 80, 30.0, 31800.0, 954000.0, 'INR', 'City center public water kiosks.'),
  (25, 'gem', 'GEM/2025/B/6001234', '2025-08-15', 'Tamil Nadu Water Supply & Drainage Board (TWAD)', 'Tamil Nadu', 'State Dept', 'Southern Cooling Systems', 'SCS-DLR-004', 'Authorized Dealer', 150, 55.0, 42400.0, 2332000.0, 'INR', 'TWAD rural community water purification points.'),
  (8, 'gem', 'GEM/2025/B/5987123', '2025-08-10', 'Military Engineer Services (MES)', 'Delhi', 'Defence', 'Voltas Limited', 'VLT-OEM-001', 'OEM', 150, 85.0, 39800.0, 3383000.0, 'INR', 'Base hospital and cantonment bulk supply.'),
  (16, 'gem', 'GEM/2025/B/5891234', '2025-07-22', 'Directorate of Education Delhi', 'Delhi', 'Education', 'Usha International', 'USH-OEM-003', 'OEM', 40, 140.0, 23500.0, 3290000.0, 'INR', 'Delhi Govt Senior Secondary Schools.')
on conflict (award_id) do nothing;
