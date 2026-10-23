-- ==============================================================================
-- BloodBridge Supabase PostgreSQL Schema
-- Run this in your Supabase Dashboard -> SQL Editor
-- ==============================================================================

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. Profiles Table (Requesters and Donors)
create table if not exists public.profiles (
    id uuid references auth.users on delete cascade primary key,
    phone varchar(20) unique not null,
    name varchar(100) not null,
    city varchar(50) not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Standby Donors Table (Registered voluntary standby donors)
create table if not exists public.standby_donors (
    id uuid default uuid_generate_v4() primary key,
    name varchar(100) not null,
    phone varchar(20) unique not null,
    blood_group varchar(5) not null check (blood_group in ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    city varchar(50) not null,
    area varchar(100),
    latitude double precision not null,
    longitude double precision not null,
    is_available boolean default true not null,
    total_donations integer default 0 not null,
    last_donated_at date,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Geospatial / Radius search index on coordinates
create index if not exists idx_donors_coords on public.standby_donors(latitude, longitude);
create index if not exists idx_donors_blood_city on public.standby_donors(blood_group, city, is_available);

-- 3. Blood Requests Table (Urgent search cases)
create table if not exists public.blood_requests (
    id uuid default uuid_generate_v4() primary key,
    reference_code varchar(20) unique not null,
    requester_id uuid references public.profiles(id) on delete set null,
    blood_group varchar(5) not null check (blood_group in ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    blood_component varchar(50) not null default 'Whole Blood',
    units_needed integer not null check (units_needed between 1 and 20),
    urgency varchar(20) not null check (urgency in ('routine', 'urgent', 'emergency')),
    hospital_name varchar(150) not null,
    hospital_area varchar(100),
    hospital_city varchar(50) not null,
    hospital_latitude double precision not null,
    hospital_longitude double precision not null,
    contact_person varchar(100) not null,
    contact_phone varchar(20) not null,
    notes text,
    status varchar(30) not null default 'searching' check (status in ('searching', 'donor_matched', 'fulfilled', 'cancelled')),
    matched_donor_id uuid references public.standby_donors(id) on delete set null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

create index if not exists idx_requests_status on public.blood_requests(status);
create index if not exists idx_requests_city on public.blood_requests(hospital_city);

-- 4. WhatsApp Dispatch & Acceptance Log Table
create table if not exists public.donor_dispatches (
    id uuid default uuid_generate_v4() primary key,
    request_id uuid references public.blood_requests(id) on delete cascade not null,
    donor_id uuid references public.standby_donors(id) on delete cascade not null,
    whatsapp_message_id varchar(100),
    status varchar(20) not null default 'dispatched' check (status in ('dispatched', 'delivered', 'accepted', 'declined', 'timeout')),
    dispatched_at timestamp with time zone default timezone('utc'::text, now()) not null,
    responded_at timestamp with time zone
);

create index if not exists idx_dispatches_request on public.donor_dispatches(request_id);

-- Row Level Security (RLS) Policies
alter table public.profiles enable row level security;
alter table public.standby_donors enable row level security;
alter table public.blood_requests enable row level security;
alter table public.donor_dispatches enable row level security;

-- Public read access for active requests (for live dashboard)
create policy "Allow public read of active blood requests"
    on public.blood_requests for select using (true);

-- Allow authenticated or public creation of emergency requests
create policy "Allow insert of blood requests"
    on public.blood_requests for insert with check (true);

-- Allow standby donors to register
create policy "Allow insert of standby donors"
    on public.standby_donors for insert with check (true);

create policy "Allow public read of standby donors"
    on public.standby_donors for select using (true);
