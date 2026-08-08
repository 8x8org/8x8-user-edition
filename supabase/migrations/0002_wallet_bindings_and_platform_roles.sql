-- 8x8 protected-beta wallet/public-address binding and platform-role model.
-- Stores public identifiers only. Never store private keys, seed phrases or signing secrets here.

create table if not exists public.platform_roles (
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('OWNER_ADMIN','PLATFORM_ADMIN','SUPPORT_OPERATOR','STANDARD_USER')),
  granted_at timestamptz not null default now(),
  granted_by text not null default 'SECURE_SERVER_PROVISIONING',
  primary key (user_id, role)
);

create table if not exists public.wallet_bindings (
  wallet_id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  eightx8_id text not null references public.profiles(eightx8_id) on update cascade on delete cascade,
  chain_family text not null check (chain_family in ('EVM','SOLANA','TON','BITCOIN','PI','8X8')),
  network text not null,
  public_address text not null,
  wallet_role text not null check (wallet_role in (
    'OWNER_TREASURY','OPERATING_TREASURY','LIQUIDITY','FEE_COLLECTION',
    'TOKEN_ADMIN','ASSET_RESERVE','AGENT_OPERATIONAL_TESTNET_ONLY','USER_SELF_CUSTODY'
  )),
  custody_mode text not null check (custody_mode in ('USER_SELF_CUSTODY','PUBLIC_ADDRESS_BINDING_ONLY','EXTERNAL_MULTISIG')),
  verification_method text not null default 'PENDING_SIGNED_CHALLENGE' check (verification_method in (
    'PENDING_SIGNED_CHALLENGE','SIGNED_CHALLENGE','PASSKEY_BOUND_SESSION','ADMIN_VERIFIED_EXTERNAL_MULTISIG'
  )),
  verified_at timestamptz,
  is_primary boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (chain_family, network, public_address)
);

create index if not exists wallet_bindings_user_idx on public.wallet_bindings(user_id);
create index if not exists wallet_bindings_eightx8_idx on public.wallet_bindings(eightx8_id);

alter table public.platform_roles enable row level security;
alter table public.wallet_bindings enable row level security;

-- Users may see their own platform role but cannot grant or modify roles from the client.
create policy "platform_roles_select_own" on public.platform_roles
  for select using (auth.uid() = user_id);

-- Users can see their own wallet bindings.
create policy "wallet_bindings_select_own" on public.wallet_bindings
  for select using (auth.uid() = user_id);

-- Client-side users may only add self-custody bindings for themselves and only for their own immutable 8x8 ID.
create policy "wallet_bindings_insert_self_custody" on public.wallet_bindings
  for insert with check (
    auth.uid() = user_id
    and wallet_role = 'USER_SELF_CUSTODY'
    and custody_mode = 'USER_SELF_CUSTODY'
    and eightx8_id = (select p.eightx8_id from public.profiles p where p.user_id = auth.uid())
  );

-- Users may remove their own self-custody binding. Privileged treasury/admin bindings are server-managed.
create policy "wallet_bindings_delete_self_custody" on public.wallet_bindings
  for delete using (
    auth.uid() = user_id
    and wallet_role = 'USER_SELF_CUSTODY'
    and custody_mode = 'USER_SELF_CUSTODY'
  );

-- Deliberately no client INSERT/UPDATE/DELETE policy for platform_roles or privileged wallet roles.
-- OWNER_ADMIN and treasury/liquidity/admin bindings must be provisioned by an authenticated server-side workflow,
-- logged in identity_audit_events, and proven by signed-wallet challenge before becoming VERIFIED.
