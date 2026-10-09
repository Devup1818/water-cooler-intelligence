-- =============================================================================
-- COOL HOME (INDIA) / FRESCO CASA - GOVT TENDER INTELLIGENCE DATABASE
-- PostgreSQL / Supabase Migration Schema
-- =============================================================================

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. BIDS TABLE: All tracked tenders (GeM + State GePNIC Portals)
-- -----------------------------------------------------------------------------
create table if not exists public.bids (
    bid_number text primary key,
    title text,
    org_name text,
    ministry text,
    dept text,
    state text,
    portal_code text default 'gem',
    source text default 'gem',
    source_url text,
    status text default 'published',
    end_date timestamptz,
    start_date timestamptz,
    capacity_class integer,
    capacity_text text,
    quantity numeric,
    est_value numeric,
    relevant smallint default 0,
    category text,
    segment text,
    created_at timestamptz default timezone('utc'::text, now()) not null,
    updated_at timestamptz default timezone('utc'::text, now()) not null
);

-- Indexes for performance
create index if not exists idx_bids_relevant on public.bids (relevant);
create index if not exists idx_bids_end_date on public.bids (end_date);
create index if not exists idx_bids_capacity on public.bids (capacity_class);
create index if not exists idx_bids_state on public.bids (state);
create index if not exists idx_bids_portal on public.bids (portal_code);

-- -----------------------------------------------------------------------------
-- 2. BID_DOCS TABLE: Parsed official tender PDFs, specs & compressor data
-- -----------------------------------------------------------------------------
create table if not exists public.bid_docs (
    bid_number text primary key references public.bids(bid_number) on delete cascade,
    pdf_path text,
    body_text text,
    fields jsonb default '{}'::jsonb,
    fetched_at timestamptz default timezone('utc'::text, now()) not null
);

-- -----------------------------------------------------------------------------
-- 3. SELLERS TABLE: Competitor & OEM Master
-- -----------------------------------------------------------------------------
create table if not exists public.sellers (
    seller_id text primary key,
    name text not null,
    seller_type text not null, -- 'OEM' or 'Authorized Dealer'
    base_state text,
    gem_seller_id text,
    msme_udyam text,
    notes text
);

-- -----------------------------------------------------------------------------
-- 4. AWARDS TABLE: Historical verified contract awards ledger
-- -----------------------------------------------------------------------------
create table if not exists public.awards (
    award_id serial primary key,
    source text default 'gem',
    tender_id text not null,
    award_date date not null,
    buyer_org text not null,
    buyer_state text,
    segment text, -- 'Railways', 'Defence', 'Municipal', 'Health', etc.
    seller_name text not null,
    seller_id text references public.sellers(seller_id),
    seller_type text,
    capacity_class integer,
    qty numeric not null,
    unit_price numeric not null,
    total_value numeric not null,
    currency text default 'INR',
    remarks text,
    source_url text,
    entered_at timestamptz default timezone('utc'::text, now()) not null
);

create index if not exists idx_awards_date on public.awards (award_date);
create index if not exists idx_awards_seller on public.awards (seller_name);
create index if not exists idx_awards_capacity on public.awards (capacity_class);

-- -----------------------------------------------------------------------------
-- 5. RUNS TABLE: Audit log of automated scraper & sync runs
-- -----------------------------------------------------------------------------
create table if not exists public.runs (
    id serial primary key,
    started_at timestamptz not null,
    ended_at timestamptz not null,
    action text not null,
    summary text
);

-- -----------------------------------------------------------------------------
-- ROW LEVEL SECURITY (RLS) POLICIES
-- -----------------------------------------------------------------------------
alter table public.bids enable row level security;
alter table public.bid_docs enable row level security;
alter table public.sellers enable row level security;
alter table public.awards enable row level security;
alter table public.runs enable row level security;

-- Allow public read-only access (for Vercel web command center)
create policy "Allow public read access on bids" on public.bids for select using (true);
create policy "Allow public read access on bid_docs" on public.bid_docs for select using (true);
create policy "Allow public read access on sellers" on public.sellers for select using (true);
create policy "Allow public read access on awards" on public.awards for select using (true);
create policy "Allow public read access on runs" on public.runs for select using (true);

-- Allow authenticated / service_role write access
create policy "Allow service role write access on bids" on public.bids for all using (auth.role() = 'service_role');
create policy "Allow service role write access on bid_docs" on public.bid_docs for all using (auth.role() = 'service_role');
create policy "Allow service role write access on sellers" on public.sellers for all using (auth.role() = 'service_role');
create policy "Allow service role write access on awards" on public.awards for all using (auth.role() = 'service_role');
create policy "Allow service role write access on runs" on public.runs for all using (auth.role() = 'service_role');
