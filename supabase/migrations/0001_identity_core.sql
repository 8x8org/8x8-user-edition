-- 8x8 OS 0.0.1 Beta protected identity core.
-- Deploy only to the canonical Supabase project after explicit cost/organization approval.

create extension if not exists pgcrypto;

create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  eightx8_id text not null unique,
  handle text unique,
  display_name text,
  bio text,
  avatar_url text,
  account_state text not null default 'ACTIVE' check (account_state in ('INVITED','ACTIVE','SUSPENDED','DELETED')),
  reality text not null default 'PUBLIC_PRESENT' check (reality in ('PRIVATE_PAST','PUBLIC_PRESENT','FUTURE_LAB')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint eightx8_id_format check (eightx8_id ~ '^8x8_[0-9a-z]{20,40}$')
);

create table if not exists public.user_consents (
  user_id uuid not null references auth.users(id) on delete cascade,
  consent_type text not null check (consent_type in ('TERMS','PRIVACY','DEVICE_CONTRIBUTION','TELEMETRY','WALLET','ECONOMY','MARKETING','VOICE','LOCATION')),
  granted boolean not null,
  policy_version text not null default '0.0.1',
  recorded_at timestamptz not null default now(),
  revoked_at timestamptz,
  primary key (user_id, consent_type)
);

create table if not exists public.user_workspaces (
  workspace_id uuid primary key default gen_random_uuid(),
  owner_user_id uuid not null references auth.users(id) on delete cascade,
  name text not null default 'My 8x8 Workspace',
  status text not null default 'ACTIVE' check (status in ('ACTIVE','SUSPENDED','DELETED')),
  reality text not null default 'PUBLIC_PRESENT' check (reality in ('PRIVATE_PAST','PUBLIC_PRESENT','FUTURE_LAB')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.identity_audit_events (
  event_id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  event_type text not null,
  event_data jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create or replace function public.make_eightx8_id()
returns text
language plpgsql
security definer
set search_path = public
as $$
declare
  candidate text;
begin
  loop
    candidate := '8x8_' || lower(encode(gen_random_bytes(15), 'hex'));
    exit when not exists (select 1 from public.profiles where eightx8_id = candidate);
  end loop;
  return candidate;
end;
$$;

create or replace function public.bootstrap_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  new_id text;
begin
  new_id := public.make_eightx8_id();
  insert into public.profiles(user_id, eightx8_id, handle, display_name)
  values (
    new.id,
    new_id,
    nullif(new.raw_user_meta_data ->> 'handle', ''),
    nullif(new.raw_user_meta_data ->> 'display_name', '')
  );
  insert into public.user_workspaces(owner_user_id) values (new.id);
  insert into public.identity_audit_events(user_id, event_type, event_data)
  values (new.id, 'ACCOUNT_BOOTSTRAPPED', jsonb_build_object('eightx8_id', new_id, 'product_version', '0.0.1'));
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.bootstrap_new_user();

alter table public.profiles enable row level security;
alter table public.user_consents enable row level security;
alter table public.user_workspaces enable row level security;
alter table public.identity_audit_events enable row level security;

create policy "profiles_select_own" on public.profiles for select using (auth.uid() = user_id);
create policy "profiles_update_own" on public.profiles for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "consents_own" on public.user_consents for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "workspaces_own" on public.user_workspaces for all using (auth.uid() = owner_user_id) with check (auth.uid() = owner_user_id);
create policy "audit_select_own" on public.identity_audit_events for select using (auth.uid() = user_id);

revoke all on function public.make_eightx8_id() from public;
revoke all on function public.bootstrap_new_user() from public;
