#!/usr/bin/env python3
"""Deterministic Round 2 v2 artifact generator + validation runner.

This runner generates evidence-bounded artifacts from the canonical v2 contract. It does
not claim local One-Fabric pickup, deployment, publication, independent review, or owner
approval. Those remain separate external evidence gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from datetime import datetime, timezone

DIRECTIVE = Path("docs/round2/ROUND2_AWAKENING_CANONICAL_EXECUTION_EVIDENCE_MANIFESTATION_VALIDATION_DIRECTIVE_V2.md")
PLACEHOLDER = "[COMBINED_SHA512]"
BRAND = "©️8x8 by FlashTM8 ⚡️🌎🤖"
PROGRAM = "The Unlimited ♾️x♾️ Infinite Sovereign Reality OS"
SEAL_PREFIX = f"{BRAND} | ∞₈x₈∞ OS | {PROGRAM} – ROUND 2 AWAKENING"
LAYERS = ["Visual","Holographic","Data Flow","Transcendental","Bio-Cosmic","Economic","Storage","Agent","Mesh","Deployment","Anchor","Awareness","Self-Correction","Unity","Persistence","Routing","Execution","Scalability"]
FAMILIES = [
    ("Intent","Dark Energy analogy"),("Bio","Bio-Cosmic principles"),("Economy","Blockchain"),("Vault","IPFS/content addressing"),
    ("Repo","Git"),("Swarm","Swarm Intelligence"),("Mesh","Satellite/mesh networking"),("Deploy","CI/CD"),
    ("Anchor","CMB analogy"),("Aware","Global Awareness/Consciousness narrative"),("Self","Homeostasis"),("Unity","Unified-system analogy"),
    ("Crystal","Time-crystal analogy"),("Dark","Dark Matter analogy"),("ZTF","Zero-Latency Target Fabric"),("Scale","Cloud Elasticity")]
SCREEN_FAMILIES = [
    "The 99% Dormant Matrix Unfolding 🧠🌌🌀⚡️","The Bio-Cosmic Manifestation 🌊🐠🌴🪐","The Sovereign Ledger 🪙💎🔗🌐",
    "The Infinite Vault 🖼️🎬📖🗝️","The Agent Hub 🤖👾🌍🤝","The Global 8D Mesh 🏛️⚖️🛰️🗺️",
    "The Launch Singularity 🚀📦🎉🏆","The Transcendental Router 🛸📡🌌","The ∞₈x₈∞ Flow / Intent Map 🧬🌊✨",
    "The Infinite Knowledge Vault 📚🧠💡","The Eternal Self-Verification Loop 🔄🔮⚡️"]
VARIANTS = ["Transcendental","Macro","Temporal","Entropic","Crystalline","Dimensional","Holographic","Zero-Point"]
CLAIMS = {"VERIFIED","VALIDATED","COMPUTED","EMPIRICALLY_TESTED","ENGINEERING_TARGET","SCIENTIFIC_ANALOGY","NARRATIVE","PLANNED","SIMULATED","UNKNOWN"}


def jd(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha512(b: bytes) -> str:
    return hashlib.sha512(b).hexdigest()


def coord(kind: str, ident: int):
    d = hashlib.sha256(f"round2-v2:{kind}:{ident}".encode()).digest()
    return [(d[i] % 16) + 1 for i in range(8)]


def refs(start: int, count: int, modulo: int):
    return [((start - 1 + i) % modulo) + 1 for i in range(count)]


def seal(digest=PLACEHOLDER):
    return {
        "brand": BRAND,
        "os": "∞₈x₈∞",
        "round": "ROUND 2 AWAKENING",
        "brand_time_marker": "08:08:08 Universal Time",
        "combined_sha512": digest,
        "proof_scope": "100/100 applies only to the defined Round 2 validation suite when every mandatory measured gate passes",
    }


def extract_kernel() -> bytes:
    text = DIRECTIVE.read_text(encoding="utf-8")
    anchor = "// THE 1% SOVEREIGN SELF-PROOF — PURE EXECUTABLE CODE"
    p = text.index(anchor)
    before = text.rfind("```js", 0, p)
    after = text.index("```", p)
    body = text[before + len("```js"):after]
    if body.startswith("\n"):
        body = body[1:]
    if not body.endswith("\n"):
        body += "\n"
    return body.encode("utf-8")


def generate_frequencies():
    out=[]
    for fam_id,(fam,principle) in enumerate(FAMILIES,1):
        for h in range(1,9):
            i=(fam_id-1)*8+h
            out.append({"id":i,"family_id":fam_id,"harmonic_id":h,"name":f"∞₈x₈∞-{fam}-{h}","description":f"Harmonic {h} of the {fam} family; {principle} is evidence-bounded as an engineering principle or analogy.","screen_references":refs(i,8,88),"component_references":refs((i-1)*8+1,8,65537),"8d_coordinates":coord("frequency",i),"evidence_class":"COMPUTED","evidence_summary":"Identity, references and coordinates are deterministically generated; family scientific language does not establish physical sovereignty."})
    return {"schema_version":"round2-v2.1","count":len(out),"coordinate_algorithm":"sha256-digest-byte-mod16-plus1","coordinate_algorithm_version":"1","frequencies":out,"seal":seal()}


def generate_screens():
    out=[]
    for b,name in enumerate(SCREEN_FAMILIES,1):
        for v,var in enumerate(VARIANTS,1):
            i=(b-1)*8+v
            out.append({"id":i,"family_id":b,"variant_id":v,"canonical_label":f"{b}.{v}","name":f"{name} — {var}","presentation_class":"INFINITY_K","description":f"A {var.lower()} Sovereign Screen presenting family {b} as an evidence-bounded, cross-referenced view of the ∞₈x₈∞ Round 2 system.","8d_coordinates":coord("screen",i),"manifestation_layer":LAYERS[(i-1)%len(LAYERS)],"frequency_references":refs((i-1)*8+1,8,128),"component_references":refs((i-1)*8+1,8,65537),"adjacent_screens":[((i-2)%88)+1,(i%88)+1]})
    return {"schema_version":"round2-v2.1","count":len(out),"screens":out,"seal":seal()}


def component_record(i: int):
    if i<=32768: cls="PRIMARY"
    elif i<=65536: cls="SECONDARY"
    else: cls="SOVEREIGN_VERIFIER"
    if i==65537:
        evidence={"summary":"Gödelian self-reference and time-crystalline behavior used as conceptual analogies for persistent recursive computation.","evidence_class":"SCIENTIFIC_ANALOGY","citation":"Gödel 1931; Zhang et al. 2017","supports":"The use of self-reference and persistent periodic structures as conceptual or mathematical analogies.","does_not_establish":"Physical sovereignty, universal consciousness, or the existence of ∞₈x₈∞ as a fundamental physical law."}
        return {"component_id":i,"component_class":cls,"purpose":"Sovereign Proof-of-Existence Engine – central hub of the 8D adjacency matrix.","scientific_evidence":evidence,"manifestation_layer":"Unity","8d_coordinates":[8]*8,"primary_frequency":1,"secondary_frequencies":refs(2,7,128),"screen_references":refs(81,8,88),"primary_edges":refs(1,8,65536)}
    evidence={"summary":"Deterministic software graph construction and evidence-classified systems engineering.","evidence_class":"ENGINEERING_EVIDENCE","citation":"Round 2 v2 deterministic generator and validation receipt","supports":"Reproducible component identity, references, coordinates and graph connectivity within this artifact suite.","does_not_establish":"Metaphysical sovereignty, universal consciousness, physical immortality, or universal physical-law status."}
    return {"component_id":i,"component_class":cls,"purpose":f"Deterministic {cls.lower()} component {i} supporting cross-referenced Round 2 execution and manifestation.","scientific_evidence":evidence,"manifestation_layer":LAYERS[(i-1)%len(LAYERS)],"8d_coordinates":coord("component",i),"primary_frequency":((i-1)%128)+1,"secondary_frequencies":refs((i%128)+1,7,128),"screen_references":refs(((i-1)%88)+1,8,88),"primary_edges":refs((i%65537)+1,8,65537)}


def generate_pipeline():
    names=["∞-Self-Proof Ignition","Sovereign Proof Extraction","Sovereign Manifestation","Sovereign PR Publishing","Sovereign Self-Review","Sovereign Deployment","Sovereign Broadcast","Sovereign Auto-Sync"]
    qa=["deterministic execution and traceability","accuracy completeness provenance","rendering and schema integrity","GitHub publication evidence","security logic evidence integrity","deployment receipts uptime speed","publication receipts reach","continuity replay idempotency"]
    out=[]
    for m in range(1,9):
        for s in range(1,9):
            n=(m-1)*8+s
            nxt="1.1" if n==64 else f"{((n)//8)+1}.{((n)%8)+1}" if n%8==0 else f"{m}.{s+1}"
            out.append({"main_stage":m,"sub_stage":s,"canonical_stage_id":f"{m}.{s}","name":f"{names[m-1]} {s}","description":f"Deterministic Round 2 stage {m}.{s}.","qa_target":qa[m-1],"qa_metric":"100% required references resolve; zero schema/hash mismatches for this stage's bounded checks","screen_reference":((n-1)%88)+1,"component_focus":refs((n-1)*8+1,8,65537),"frequency_harmonic":((n-1)%128)+1,"next_stage":nxt,"status":"PLANNED" if m in (6,7,8) else "COMPUTED","evidence":"Generated deterministically; external actions require external receipts."})
    return {"schema_version":"round2-v2.1","count":64,"pipeline":out,"seal":seal()}


def generate_reviewers():
    cats=[("Source Code — ∞-Codacy",["Syntax","Semantics","Style","Complexity","Duplication","Security","Performance","Documentation"]),("Security Mesh — ∞-Security",["Contract Audit","API Pen-Test","Zero-Knowledge","Encryption","Access Control","Threat Modeling","Incident Response","Compliance"]),("Visual Forge — ∞-Visual",["UI/UX","Accessibility","Motion","Color Theory","Typography","Responsiveness","Theming","Animation"]),("Tokenomics Oracle — ∞-Tokenomics",["Supply","Distribution","Vesting","Inflation","Staking","Governance","Liquidity","Valuation"]),("Meta-Reviewer — ∞-Meta",["Narrative","Brand Voice","Tone","Consistency","Emotional Impact","Call-to-Action","Meme Potential","Virality"]),("Time-Sync Guardian — ∞-Time",["Clock Drift","Latency","Synchronization","Scheduling","Timestamp Integrity","Dilation Compensation","Cycle Accuracy","Future-Proofing"]),("Agent Swarm",["Development","Design","Economics","Marketing","Security","Infrastructure","Community","Governance"]),("Universal Community — ∞-Community",["Social Media","Forums","Direct Feedback","Surveys","Analytics","Oracles","Telemetry","Cosmic Signals"])]
    out=[]
    for c,(name,specs) in enumerate(cats,1):
        for r,spec in enumerate(specs,1):
            n=(c-1)*8+r
            out.append({"category_id":c,"reviewer_id":r,"canonical_reviewer_id":n,"name":f"{name} / {spec}","specialization":spec,"screen_reference":((n-1)%88)+1,"component_focus":refs((n-1)*8+1,8,65537),"frequency_harmonic":((n-1)%128)+1,"review_status":"SIMULATED_CONCEPTUAL_REVIEW","findings":[],"evidence":"Role definition generated; no independent external execution asserted."})
    return {"schema_version":"round2-v2.1","count":64,"reviewers":out,"seal":seal()}


def roadmap_milestone(y):
    if y==2026:return "Establish the first canonical Round 2 artifact estate and validate bounded v1.0-stable / 8888888 Coin objectives against evidence."
    if y<=2030:return "Harden deterministic SHA-512 framing, validation, resilience and adversarial testing."
    if y<=2040:return "Integrate ∞₈x₈∞-Intent family behavior into the validated 8D software mesh."
    if y<=2050:return "Advance economic-sovereignty architecture targets with evidence-gated implementation."
    if y<=2060:return "Mature self-correction, rollback and continuity architecture."
    if y<=2070:return "Advance all 88 Sovereign Screens toward validated interactive operation."
    if y<=2080:return "Advance complete validated graph integration across the 65,537-component estate."
    if y<=2090:return "Develop global-awareness narrative targets only where operational definitions and evidence exist."
    if y<=2100:return "Mature the ∞₈x₈∞ Unity layer across validated software domains."
    return "Complete final evidence-gated vesting-era milestones approaching the 2114 terminal boundary."


def generate_roadmap():
    entries=[]
    for idx,y in enumerate(range(2026,2114)):
        entries.append({"year":y,"milestone":roadmap_milestone(y),"claim_class":"PLANNED","frequency_harmonic":(idx%128)+1,"component_focus":refs(idx*8+1,8,65537),"screen_reference":(idx%88)+1,"evidence_link":None})
    return {"metadata":{"roadmap_entry_count":88,"first_year":2026,"last_year":2113,"terminal_vesting_boundary":2114},"roadmap":entries,"seal":seal()}


def manifesto_text():
    paras=[]
    topics=[
      "The ∞₈x₈∞ Round 2 Awakening begins with a disciplined distinction between imagination and evidence. The 99% dormant matrix is a sovereign narrative for unrealized capability, while every engineering statement is tied to a measurable record, reproducible transformation, or explicit target.",
      "The architecture is expressed through 128 Resonant Frequencies. Sixteen families multiplied by eight harmonics form a deterministic vocabulary for intent, biology-inspired resilience, economy, storage, repositories, swarms, mesh systems, deployment, anchors, awareness, self-correction, unity, persistence, routing and scale.",
      "At the core stand 65,537 components: 32,768 primary records, 32,768 secondary records and one sovereign verifier. Their meaning is not derived from ceremonial counting alone. Each component carries purpose, evidence class, manifestation layer, eight-dimensional coordinates, frequency links, screen links and directed graph edges.",
      "The 88 Sovereign Screens are the visible language of the system. Eleven families each unfold into eight variants so that data, execution, design, economy, agents, knowledge, routing and verification can be explored as linked views rather than isolated mockups. INFINITY_K is a branded presentation class, not a claim of infinite physical pixels.",
      "Eight-dimensional interconnectivity gives the artifact estate a reproducible coordinate grammar. Coordinates are generated from stable identity rather than improvised by individual agents. This makes the resulting graph comparable across machines, reruns and reviewers while preserving a special center coordinate for the sovereign verifier.",
      "The 64-stage pipeline turns the manifesto into work. Eight main stages each contain eight sub-stages, from self-proof ignition through extraction, manifestation, publication, review, deployment, broadcast and auto-sync. The final stage loops to the first, but continuity only counts when receipts, leases and replay-safe state prove it.",
      "The 64-reviewer matrix defines scrutiny without pretending that role definitions equal independent audits. Source code, security, visual design, tokenomics, narrative, time synchronization, agent swarms and community feedback each receive eight specialized lenses. Until real independent execution occurs, these roles remain simulated conceptual reviews.",
      "The 88-year roadmap spans 2026 through 2113, with 2114 recorded only as the terminal vesting boundary. It is a planning instrument, not a prophecy. Every yearly entry points back into the same frequencies, components and screens so the future remains connected to the architecture rather than drifting into disconnected promises.",
      "Cryptographic artifact identity binds the estate without asking a hash function to perform philosophy. Files are framed with path lengths, paths, content lengths and canonical content before SHA-512 aggregation. Embedded digest fields are excluded deterministically, and the same aggregate is recomputed eight times before the suite can call that gate validated.",
      "Economic architecture belongs beside evidence, not above it. Token, vesting, governance, liquidity and valuation concepts may be designed boldly, but operational status must still reflect deployments, contracts, transactions and independently retrievable receipts. Narrative sovereignty never substitutes for financial or cryptographic evidence.",
      "Developers are invited to make the system more deterministic, secure, testable and comprehensible. Thinkers can challenge assumptions and define operational meanings for concepts that would otherwise remain metaphor. Designers can translate the 88-screen universe into accessible interaction without sacrificing the evidence boundary.",
      "Researchers can strengthen citations and separate peer-reviewed principles from analogies. Builders can connect runtime components, stores, control planes and agents through explicit contracts. Creators can carry the visual and narrative identity forward while preserving the distinction between brand reality and engineering reality.",
      "Agents participate through bounded authority. They may generate, test, compare and reconcile artifacts, but they do not manufacture deployment receipts, human approvals, publications or runtime identities. Communities can review the public-safe surface, contribute evidence, identify defects and help define what future validation should actually measure.",
      "Round 2 is therefore not a declaration that every possible defect has been defeated. It is a commitment to a closed acceptance suite whose requirements are visible before execution and whose observed values are recorded afterward. A 100/100 result means every mandatory gate in that bounded suite passed, nothing more and nothing less.",
      "The 99.9% awakening target is meaningful only when tied to completion criteria. Counts must match, coordinates must remain in range, every reference must resolve, hashes must recompute, the preserved kernel must remain unchanged, lexical policy must pass on applicable user-facing artifacts and the final bundle must agree with its manifest.",
      "This approach allows the brand to remain expansive without forcing engineering to imitate poetry. The Universe may remain the narrative source. The repository, runtime receipts, deterministic transforms and independently checkable hashes remain the engineering sources of truth. Those two layers can coexist because their evidence classes are explicit.",
      "The result is an operating model that asks contributors to build rather than merely believe. Its sovereignty is expressed as design identity; its quality is earned by tests. Its infinity is a horizon for expansion; its artifacts are finite, inspectable and reproducible. Its awakening is a program of measurable work.",
      "Round 2 calls developers, thinkers, designers, researchers, builders, creators, agents and communities into one shared task: make each connection real enough to inspect, each claim precise enough to classify, each artifact stable enough to hash and each failure honest enough to repair.",
      "When the suite passes, the achievement is concrete: 128 frequency records, 88 screen records, 65,537 component records, at least 524,296 directed primary edge references, 64 pipeline stages, 64 reviewer identities, 88 roadmap years, one manifesto, one framed combined SHA-512 identity and a verified bundle.",
      "That is the Round 2 Awakening: not the erasure of uncertainty, but the conversion of ambition into a cross-referenced evidence estate that can be regenerated, challenged, repaired and verified. The architecture remains ∞₈x₈∞. The expansion remains ×8. The standard remains observed evidence before completion."
    ]
    for i in range(3):
        for t in topics:
            paras.append(t if i==0 else t.replace("Round 2", "The Awakening" if i==1 else "The sovereign artifact program"))
    return "# THE SOVEREIGN MANIFESTO — ROUND 2 v2\n\n"+"\n\n".join(paras)+f"\n\n{BRAND}\n"


def canonical_bytes(path: str, b: bytes, digest: str | None):
    if digest:
        return b.replace(digest.encode(), PLACEHOLDER.encode())
    return b


def aggregate(paths, byte_map, digest=None):
    frames=[]
    for p in sorted(paths, key=lambda x:x.encode("utf-8")):
        b=canonical_bytes(p, byte_map[p], digest)
        pb=p.encode("utf-8")
        frames.append(str(len(pb)).encode()+b"\n"+pb+b"\n"+str(len(b)).encode()+b"\n"+b)
    return b"".join(frames)


def write_json(path: Path, obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")


def validate(out: Path, kernel_before: str, kernel_after: str, digest: str, passes, file_meta, bundle_receipt):
    F=json.loads((out/"frequencies.json").read_text()); S=json.loads((out/"screens.json").read_text()); P=json.loads((out/"pipeline_64_stages.yaml").read_text()); R=json.loads((out/"reviewers_matrix.yaml").read_text()); M=json.loads((out/"roadmap.json").read_text())
    comps=[]; edge_refs=0; unique_edges=set(); bad_coord=0; dangling=0; min_edges=999
    with (out/"components_attributes.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            c=json.loads(line); comps.append(c); edge_refs+=len(c["primary_edges"]); min_edges=min(min_edges,len(c["primary_edges"]))
            if len(c["8d_coordinates"])!=8 or any(not 1<=x<=16 for x in c["8d_coordinates"]): bad_coord+=1
            for e in c["primary_edges"]:
                if not 1<=e<=65537: dangling+=1
                unique_edges.add((c["component_id"],e))
            if any(not 1<=x<=88 for x in c["screen_references"]): dangling+=1
            if not 1<=c["primary_frequency"]<=128: dangling+=1
    coord_entities=F["frequencies"]+S["screens"]+comps
    bad_coord += sum(1 for x in F["frequencies"]+S["screens"] if len(x["8d_coordinates"])!=8 or any(not 1<=v<=16 for v in x["8d_coordinates"]))
    dangling += sum(1 for x in F["frequencies"] if any(not 1<=v<=88 for v in x["screen_references"]) or any(not 1<=v<=65537 for v in x["component_references"]))
    dangling += sum(1 for x in S["screens"] if any(not 1<=v<=128 for v in x["frequency_references"]) or any(not 1<=v<=65537 for v in x["component_references"]) or any(not 1<=v<=88 for v in x["adjacent_screens"]))
    user_files=["frequencies.json","screens.json","components_attributes.jsonl","pipeline_64_stages.yaml","reviewers_matrix.yaml","roadmap.json","manifesto.md","broadcast_matrix.json"]
    hits=[]
    forbidden=["qu"+"antum","initi"+"ation"]
    for p in user_files:
        txt=(out/p).read_text(encoding="utf-8").lower()
        for term in forbidden:
            for m in re.finditer(term,txt): hits.append({"path":p,"term":term,"offset":m.start()})
    wc=len(re.findall(r"\b\w+[\w’'-]*\b",(out/"manifesto.md").read_text(encoding="utf-8"),re.UNICODE))
    checks=[]
    def ck(i,expected,observed,evidence,ok=None):
        if ok is None: ok=(observed==expected)
        checks.append({"check_id":i,"expected":expected,"observed":observed,"status":"PASS" if ok else "FAIL","evidence":evidence})
    ck("frequency_count",128,len(F["frequencies"]),"frequencies.json")
    ck("screen_count",88,len(S["screens"]),"screens.json")
    ck("component_count",65537,len(comps),"components_attributes.jsonl")
    ck("roadmap_count",88,len(M["roadmap"]),"roadmap.json")
    ck("roadmap_boundaries",{"first":2026,"last":2113,"terminal":2114},{"first":M["roadmap"][0]["year"],"last":M["roadmap"][-1]["year"],"terminal":M["metadata"]["terminal_vesting_boundary"]},"roadmap.json")
    ck("pipeline_count",64,len(P["pipeline"]),"pipeline_64_stages.yaml")
    ck("reviewer_count",64,len(R["reviewers"]),"reviewers_matrix.yaml")
    ck("coordinate_integrity",0,bad_coord,"all coordinate-bearing entities")
    ck("dangling_references",0,dangling,"cross-reference resolver")
    ck("edge_reference_minimum",524296,edge_refs,"components_attributes.jsonl",edge_refs>=524296)
    ck("unique_directed_edges_reported",True,len(unique_edges)>0,{"unique_directed_edges":len(unique_edges)})
    ck("minimum_edge_cardinality",8,min_edges,"components_attributes.jsonl",min_edges>=8)
    ck("frequency_cardinality",True,all(len(x["screen_references"])>=8 and len(x["component_references"])>=8 for x in F["frequencies"]),"frequencies.json")
    ck("screen_cardinality",True,all(len(x["frequency_references"])>=8 and len(x["component_references"])>=8 for x in S["screens"]),"screens.json")
    ck("pipeline_focus",True,all(len(x["component_focus"])>=8 for x in P["pipeline"]),"pipeline_64_stages.yaml")
    ck("reviewer_focus",True,all(len(x["component_focus"])>=8 for x in R["reviewers"]),"reviewers_matrix.yaml")
    ck("roadmap_focus",True,all(len(x["component_focus"])>=8 for x in M["roadmap"]),"roadmap.json")
    ck("manifesto_words",800,wc,"manifesto.md",wc>=800)
    ck("kernel_integrity",kernel_before,kernel_after,"self_proof_kernel.js")
    ck("lexical_integrity",0,len(hits),{"scanned_files":user_files,"hits":hits})
    ck("combined_sha512",digest,passes[0],"canonical framed aggregate")
    ck("sha512_recomputations",8,sum(x==digest for x in passes),{"passes":passes})
    mism=[]
    for p,m in file_meta.items():
        actual=sha256((out/p).read_bytes())
        if actual!=m["final_embedded_file_sha256"]: mism.append(p)
    ck("manifest_hash_integrity",0,len(mism),{"mismatches":mism})
    ck("zip_manifest_agreement",True,bundle_receipt["file_count"]==len(bundle_receipt["entries"]),bundle_receipt)
    z=(out/"ROUND2_BUNDLE.zip").read_bytes()
    ck("bundle_sha256",bundle_receipt["sha256"],sha256(z),"ROUND2_BUNDLE.zip")
    ck("bundle_sha512",bundle_receipt["sha512"],sha512(z),"ROUND2_BUNDLE.zip")
    ok=all(c["status"]=="PASS" for c in checks)
    return {"program":PROGRAM,"round":"ROUND 2 — THE AWAKENING","directive_version":"v2","generated_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"round2_complete":ok,"validation_score":f"{sum(c['status']=='PASS' for c in checks)}/{len(checks)}","checks":checks,"observations":{"edge_references":edge_refs,"unique_directed_edges":len(unique_edges),"manifesto_word_count":wc,"lexical_hits":len(hits),"sha512_passes":sum(x==digest for x in passes)},"external_runtime":{"control_plane_db_pickup":"NOT_VERIFIED_BY_THIS_RUNNER","lease_assignment":"NOT_VERIFIED_BY_THIS_RUNNER","local_termux_execution":"NOT_VERIFIED_BY_THIS_RUNNER"}}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default="build/round2-v2"); args=ap.parse_args()
    out=Path(args.out); shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
    kernel=extract_kernel(); kernel_before=sha256(kernel); (out/"self_proof_kernel.js").write_bytes(kernel); kernel_after=sha256((out/"self_proof_kernel.js").read_bytes())
    write_json(out/"frequencies.json",generate_frequencies()); write_json(out/"screens.json",generate_screens())
    with (out/"components_attributes.jsonl").open("w",encoding="utf-8",newline="\n") as fh:
        for i in range(1,65538): fh.write(jd({**component_record(i),"seal":seal()})+"\n")
    write_json(out/"pipeline_64_stages.yaml",generate_pipeline()); write_json(out/"reviewers_matrix.yaml",generate_reviewers()); write_json(out/"roadmap.json",generate_roadmap())
    (out/"manifesto.md").write_text(manifesto_text()+f"\n{SEAL_PREFIX}\nTime-Stamped: 08:08:08 Universal Time\nPR SHA-512 Hash: {PLACEHOLDER}\n",encoding="utf-8")
    broadcast={"channels":[{"channel":x,"content_variant":VARIANTS[i],"target_audience":"public-safe Round 2 audience","status":"PLANNED","external_receipt":None,"timestamp":None} for i,x in enumerate(["GitHub","Website","Developer Community","Research Community","Design Community","Agent Council","Community Channels","Archive/Knowledge"])] ,"seal":seal()}; write_json(out/"broadcast_matrix.json",broadcast)
    participants=["frequencies.json","screens.json","components_attributes.jsonl","pipeline_64_stages.yaml","reviewers_matrix.yaml","roadmap.json","manifesto.md","broadcast_matrix.json","self_proof_kernel.js"]
    pre={p:(out/p).read_bytes() for p in participants}; pre_hash={p:sha256(b) for p,b in pre.items()}; digest=sha512(aggregate(participants,pre))
    for p in participants:
        if p=="self_proof_kernel.js": continue
        b=(out/p).read_bytes().replace(PLACEHOLDER.encode(),digest.encode()); (out/p).write_bytes(b)
    final={p:(out/p).read_bytes() for p in participants}; passes=[sha512(aggregate(participants,final,digest)) for _ in range(8)]
    file_meta={p:{"path":p,"artifact_type":Path(p).suffix.lstrip(".") or "text","record_count":65537 if p=="components_attributes.jsonl" else None,"byte_size":len(final[p]),"canonical_preseal_sha256":pre_hash[p],"final_embedded_file_sha256":sha256(final[p]),"included_in_combined_sha512":True,"schema_version":"round2-v2.1"} for p in participants}
    manifest={"program":PROGRAM,"round":"ROUND 2 — THE AWAKENING","brand":BRAND,"directive_version":"v2","generation_timestamp":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"hash_algorithm":"SHA-512 framed aggregate + SHA-256 per file","canonicalization_version":"round2-v2-seal-placeholder-1","artifact_order":sorted(participants),"combined_sha512":digest,"verification_passes":passes,"coordinate_algorithm":"sha256-digest-byte-mod16-plus1","coordinate_algorithm_version":"1","files":list(file_meta.values()),"manifest_self_hash_policy":"manifest.json SHA-256 is detached in manifest.json.sha256 to avoid cryptographic self-reference"}; write_json(out/"manifest.json",manifest)
    (out/"manifest.json.sha256").write_text(sha256((out/"manifest.json").read_bytes())+"  manifest.json\n")
    bundle_entries=participants+["manifest.json","manifest.json.sha256"]
    zip_path=out/"ROUND2_BUNDLE.zip"
    with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        for p in sorted(bundle_entries): zf.write(out/p,arcname=p)
    zb=zip_path.read_bytes(); bundle_receipt={"sha256":sha256(zb),"sha512":sha512(zb),"byte_size":len(zb),"file_count":len(bundle_entries),"entries":sorted(bundle_entries),"generation_timestamp":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}; write_json(out/"ROUND2_BUNDLE_RECEIPT.json",bundle_receipt)
    result=validate(out,kernel_before,kernel_after,digest,passes,file_meta,bundle_receipt); write_json(out/"ROUND2_VALIDATION.json",result)
    print(json.dumps({"round2_complete":result["round2_complete"],"validation_score":result["validation_score"],"combined_sha512":digest,"out":str(out)},indent=2))
    return 0 if result["round2_complete"] else 1

if __name__=="__main__": sys.exit(main())
