# ©8x8 One Fabric World — private prelaunch plugin v0.2.0

This source-only release upgrades the existing `8x8-one-fabric-world` plugin identity. It retains OAuth-protected public read-only MCP tools and adds the all-in-one 19-domain User Edition catalog, 8x8 ID onboarding guide, user agent archetypes, usage-plan targets, connector consent guidance and a responsive MCP Apps User Hub.

**Not a production login, payment, broker, signed wallet, device or publishing server.** OAuth environment must be configured with a real IdP, a correct JWKS and correct resource-specific signed access tokens before even the read-only catalog MCP responds. Tenant/RLS authorization beyond the public catalog is not implemented in this plugin.

Repo: https://github.com/8x8org/8x8-user-edition ; identity contract: https://github.com/8x8org/8x8-user-edition/pull/200

The original MCP endpoint descriptor remains a prelaunch target; installing this plugin neither deploys that URL nor requests access to other plugins.

## Verify

`node --test tests/public-mcp.test.mjs`

25 adversarial and contract tests, including OAuth issuer/audience/signature, protected resource metadata, tool boundaries and UI resource. No automated writes or network deliveries.
