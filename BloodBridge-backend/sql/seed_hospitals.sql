-- ==============================================================================
-- BloodBridge: Seed Data for Hospital Blood Banks & Emergency Cases
-- Run this in your Supabase Dashboard -> SQL Editor
-- ==============================================================================

-- 1. Create Hospital Blood Banks Table
create table if not exists public.hospital_blood_banks (
    id varchar(50) primary key,
    name varchar(150) not null,
    city varchar(50) not null,
    area varchar(100) not null,
    province varchar(50) not null,
    phone varchar(30) not null,
    hours varchar(100) not null default '24/7 Emergency Transfusion Desk',
    latitude double precision not null,
    longitude double precision not null,
    services text[] not null default '{}',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS and public read
alter table public.hospital_blood_banks enable row level security;

create policy "Allow public read of hospital blood banks"
    on public.hospital_blood_banks for select using (true);

-- 2. Populate 20+ Verified Hospital Blood Banks across Pakistan
insert into public.hospital_blood_banks (id, name, city, area, province, phone, hours, latitude, longitude, services)
values
    -- KARACHI
    ('bb-khi-1', 'JPMC Blood Bank & Transfusion Center', 'Karachi', 'Rafiqui Shaheed Road, Karachi Cantt', 'Sindh', '021-99201300', '24/7 Emergency Transfusion Desk', 24.8532, 67.0457, ARRAY['Emergency Trauma OT', 'Platelets', 'Component Separation', 'Direct Replacement']),
    ('bb-khi-2', 'The Indus Hospital Blood Center', 'Karachi', 'Korangi Crossing, Korangi', 'Sindh', '021-111111880', '24/7 Central Blood Screening', 24.8239, 67.1264, ARRAY['100% Voluntarily Screened', 'NAT Testing', 'Platelet Apheresis']),
    ('bb-khi-3', 'Civil Hospital Karachi (CHK) Blood Transfusion', 'Karachi', 'Baba-e-Urdu Road, Saddar', 'Sindh', '021-99215740', '24/7 Government Trauma Care', 24.8575, 67.0094, ARRAY['Whole Blood', 'Plasma Clotting', 'Emergency Ward Support']),
    ('bb-khi-4', 'Fatimid Foundation Karachi', 'Karachi', '393 Britto Road, Garden East', 'Sindh', '021-32225284', '8:00 AM - 10:00 PM Daily', 24.8785, 67.0289, ARRAY['Thalassemia & Hemophilia Specialized Support', 'Free Pediatric Units']),
    ('bb-khi-5', 'Liaquat National Hospital Blood Bank', 'Karachi', 'National Stadium Road, Gulshan-e-Iqbal', 'Sindh', '021-111456456', '24/7 Emergency Transfusion Desk', 24.8933, 67.0678, ARRAY['Apheresis', 'Cross-Match', 'Trauma Resuscitation']),

    -- LAHORE
    ('bb-lhr-1', 'Shaukat Khanum Memorial Blood Center', 'Lahore', '7A Block R-3, Johar Town', 'Punjab', '042-35905000', '24/7 Oncology Transfusion Services', 31.4725, 74.2691, ARRAY['Apheresis Platelets', 'NAT Screened PRBC', 'Plasma Exchange']),
    ('bb-lhr-2', 'Services Hospital Lahore Central Blood Bank', 'Lahore', 'Ghaus-ul-Azam Road, Shadman', 'Punjab', '042-99203402', '24/7 Emergency Blood Desk', 31.5432, 74.3341, ARRAY['Trauma OT Supply', 'Fresh Frozen Plasma', 'Red Cell Concentrates']),
    ('bb-lhr-3', 'Mayo Hospital Blood Transfusion Services', 'Lahore', 'Hospital Road, Anarkali', 'Punjab', '042-99211100', '24/7 State Trauma Blood Facility', 31.5721, 74.3167, ARRAY['Accident Emergency', 'General Surgery Reserves', 'Pediatric Blood']),
    ('bb-lhr-4', 'Fatimid Foundation Lahore', 'Lahore', '530-N Samanabad, Poonch Road', 'Punjab', '042-37582544', '8:00 AM - 10:00 PM Daily', 31.5367, 74.3012, ARRAY['Thalassemia Regular Exchange', 'Hemophilia Factor VIII']),

    -- ISLAMABAD & RAWALPINDI
    ('bb-isb-1', 'PIMS Hospital Central Blood Bank', 'Islamabad', 'G-8/3, Sector G-8', 'Islamabad Capital', '051-9261170', '24/7 Federal Emergency Supply', 33.7045, 73.0567, ARRAY['Whole Blood', 'Emergency Trauma Support', 'FFP Plasma']),
    ('bb-isb-2', 'Shifa International Hospital Blood Bank', 'Islamabad', 'Pitras Bukhari Road, H-8/4', 'Islamabad Capital', '051-8463000', '24/7 Tertiary Transfusion Care', 33.6792, 73.0784, ARRAY['Leukodepleted Blood', 'Single Donor Platelets', 'Irradiated Components']),
    ('bb-rwp-1', 'Holy Family Hospital Blood Center', 'Rawalpindi', 'Holy Family Road, Satellite Town', 'Punjab', '051-9290321', '24/7 Emergency Services', 33.6331, 73.0712, ARRAY['Dengue Emergency Platelets', 'Obstetric Hemorrhage Units']),
    ('bb-rwp-2', 'Benazir Bhutto Hospital (BBH) Blood Bank', 'Rawalpindi', 'Murree Road, Asghar Mall', 'Punjab', '051-9290301', '24/7 Trauma Reserve', 33.6189, 73.0645, ARRAY['Surgical Blood Reservations', 'Universal O- Emergency Stash']),

    -- HYDERABAD
    ('bb-hyd-1', 'LUMHS Diagnostic & Research Blood Bank', 'Hyderabad', 'Civil Hospital Road, Saddar', 'Sindh', '022-9210207', '24/7 Regional Emergency Hub', 25.3942, 68.3685, ARRAY['24/7 Cross-Match', 'Component Separation', 'Trauma Supply']),
    ('bb-hyd-2', 'Red Crescent Regional Blood Center', 'Hyderabad', 'Near St. Bonaventure School, Saddar', 'Sindh', '022-2781442', '24/7 Voluntary Testing Center', 25.3881, 68.3619, ARRAY['Screened Voluntary Whole Blood', 'Platelets']),

    -- PESHAWAR
    ('bb-pesh-1', 'Lady Reading Hospital (LRH) Blood Bank', 'Peshawar', 'Soekarno Square, Andar Shehr', 'Khyber Pakhtunkhwa', '091-9211430', '24/7 Provincial Emergency Desk', 34.0094, 71.5732, ARRAY['Trauma Emergency', 'Platelet Apheresis', 'Cross Matching']),
    ('bb-pesh-2', 'Khyber Teaching Hospital (KTH) Blood Bank', 'Peshawar', 'University Road, University Town', 'Khyber Pakhtunkhwa', '091-9216340', '24/7 Surgical Support', 33.9982, 71.4889, ARRAY['Elective Surgery Reserve', 'Burn & Trauma Resuscitation']),

    -- MULTAN
    ('bb-mul-1', 'Nishtar Hospital Blood Bank', 'Multan', 'Nishtar Road, Gillani Colony', 'Punjab', '061-9200231', '24/7 South Punjab Trauma Hub', 30.1887, 71.4429, ARRAY['Mass Casualty Reserve', 'Leukocyte Filtered PRBC']),

    -- QUETTA
    ('bb-qta-1', 'Sandeman Provincial Hospital Blood Bank', 'Quetta', 'Jinnah Road, City Center', 'Balochistan', '081-9202022', '24/7 Provincial Trauma Reserve', 30.1956, 66.9989, ARRAY['Emergency Trauma Supply', 'Whole Blood Units']),

    -- FAISALABAD
    ('bb-fsd-1', 'Allied Hospital Central Blood Center', 'Faisalabad', 'Jail Road, Faisalabad', 'Punjab', '041-9210080', '24/7 District Emergency Care', 31.4289, 73.0792, ARRAY['High Volume Trauma OT', 'Platelet Concentrates'])
on conflict (id) do update set
    name = excluded.name,
    city = excluded.city,
    area = excluded.area,
    province = excluded.province,
    phone = excluded.phone,
    hours = excluded.hours,
    latitude = excluded.latitude,
    longitude = excluded.longitude,
    services = excluded.services;

-- 3. Populate Initial Active Emergency Cases into blood_requests
insert into public.blood_requests (
    reference_code, blood_group, blood_component, units_needed, urgency,
    hospital_name, hospital_area, hospital_city, hospital_latitude, hospital_longitude,
    contact_person, contact_phone, notes, status
) values
    ('BB-KHI-4812', 'O+', 'Whole Blood', 2, 'emergency', 'JPMC Karachi (Trauma OT-3)', 'Rafiqui Shaheed Road', 'Karachi', 24.8532, 67.0457, 'Tariq Memon', '3001234567', 'Patient undergoing emergency surgery, immediate cross-match sample ready at desk.', 'searching'),
    ('BB-LHR-2910', 'B-', 'Platelets', 3, 'urgent', 'Shaukat Khanum Memorial Hospital', 'Johar Town', 'Lahore', 31.4725, 74.2691, 'Dr. Arsalan', '3029876543', 'Oncology patient requiring single donor apheresis platelets.', 'searching'),
    ('BB-ISB-7741', 'A+', 'Red Blood Cells (PRBC)', 1, 'emergency', 'PIMS Hospital Islamabad (Emergency OT)', 'Sector G-8/3', 'Islamabad', 33.7045, 73.0567, 'Major Farooq', '3015551234', 'Road traffic trauma emergency case, attendant at blood bank counter.', 'searching'),
    ('BB-HYD-5103', 'O-', 'Whole Blood', 2, 'emergency', 'LUMHS Civil Hospital Hyderabad', 'Saddar', 'Hyderabad', 25.3942, 68.3685, 'Bilal Soomro', '3034448899', 'Universal donor urgent requirement for emergency surgery.', 'searching'),
    ('BB-PES-8319', 'AB+', 'Fresh Frozen Plasma', 4, 'routine', 'Lady Reading Hospital Peshawar', 'Andar Shehr', 'Peshawar', 34.0094, 71.5732, 'Gul Khan', '3047779911', 'Elective cardiovascular surgery reservation.', 'searching')
on conflict (reference_code) do nothing;

-- 4. Populate Initial Standby Donors across Cities
insert into public.standby_donors (
    name, phone, blood_group, city, area, latitude, longitude, is_available, total_donations
) values
    ('Hamza Tariq Shaikh', '3019827140', 'O+', 'Karachi', 'Clifton / DHA', 24.8250, 67.0350, true, 7),
    ('Daniyal Ali Memon', '3023344556', 'O+', 'Karachi', 'Saddar / Cantt', 24.8550, 67.0150, true, 4),
    ('Zeeshan Ahmed Khan', '3007654321', 'O-', 'Karachi', 'Gulshan-e-Iqbal', 24.9120, 67.0850, true, 11),
    ('Bilal Soomro', '3034448899', 'B+', 'Hyderabad', 'Qasimabad', 25.4050, 68.3450, true, 5),
    ('Usman Farooq', '3041122334', 'A+', 'Lahore', 'Model Town', 31.4850, 74.3200, true, 3),
    ('Mustafa Qureshi', '3055566778', 'A-', 'Islamabad', 'F-7 Markaz', 33.7210, 73.0550, true, 6)
on conflict (phone) do nothing;
