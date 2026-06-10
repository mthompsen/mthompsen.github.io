---
layout: post
title: "Map and Fortress: Why I Built Castellan"
date: 2026-06-10 13:30:00 -0500
categories: [security, projects]
tags: [nist, compliance, rmf, oscal, python]
---

A castellan was an officer in charge of a fortress's defenses. Not the officer that drew the fortress on parchment, and not the officer that filed that parchment away in an archive. The officer that walked the walls, checked the gates, counted the stores, and then informed their lord what was actually present on the fortress grounds. I built a command line tool called [Castellan](https://github.com/mthompsen/castellan) because what passes for modern security compliance is overflowing with parchment, and lacking in wall-walking. Here, I explain what gap the tool fills, how its components work together, and what a 13th century Dominican friar was doing popping into my head during development.

## The two worlds problem

If you've never been involved in government security compliance, here's the general structure. U.S. Federal systems (and many state, municipal, and contractor systems that mimic them) get authorized under the NIST Risk Management Framework (RMF). For our purposes, only four of its steps are relevant:

![The four RMF steps: categorize, select, implement, assess](/assets/images/castellan-rmf-steps.svg)

Controls are drawn from a catalog published by NIST, called SP 800-53, and are roughly a thousand specific requirements, such as AC-6 (least privilege) or AU-2 (event logging). A System Security Plan (SSP) documents how each applicable control is implemented, and a Plan of Action and Milestones (POA&M) documents what is still not in place and when it will be.

Herein lies the problem. The management component of this work exists in documentation: catalogs, plans, spreadsheets, narrative reports. The engineering component exists as actual configuration: an sshd_config file, the file permissions on /etc/shadow, or whether the auditd daemon is actually running. The two describe the same system, but in most organizations, the link between them is made manually: someone reads a control description, squints at a server, or sometimes, doesn't even squint at all. The behemoth commercial GRC platforms address this by building enormous apparatuses. The scanners at the other end (CIS benchmarks, STIG tools) produce mounds of technical data lacking clear ties to the controls documented in the paperwork. This explicit connection ("this check proves that control") is exactly the part that is most vulnerable to assessor scrutiny and most likely to be implicit. Castellan makes that connection concrete, auditable, and tiny.

## What Aquinas had to do with it

Thomas Aquinas defines truth as adaequatio rei et intellectus, the conformity of the intellect with the thing. A claim is true if what the mind asserts is what actually exists. The thing exists irrespective of your claim, and truth and falsehood lie solely in the nature of the claims we make about that thing. Compliance documents are bundles of these claims. If an SSP states that audit logging has been implemented, that statement is a claim about a real-world machine. The server neither knows nor cares what the binder says; the claim is true or false depending on whether it matches the reality of the machine. Many compliance failures are simple: documents stop matching their real-world counterparts, through accident, wishful thinking, or deliberate dishonesty.

Aquinas also proposed a term for making claims with insufficient proof: rash judgment, a fault even when the claim happens to be correct. That idea was foundational to a key design principle of the tool.

## The pipeline, end to end

Running a single command, `castellan report system.yaml`, kicks off the entire process, generating a 6-artifact evidence package.

![The Castellan pipeline: six stages from system YAML to the evidence package](/assets/images/castellan-pipeline.svg)

I'll walk through each stage:

**Categorize.** You start by describing your system in a short YAML file that details what it is, who owns it, and the types of information it processes. According to FIPS 199, each type of information has confidentiality, integrity, and availability scores (low, moderate, or high), and the system takes on the highest score among all the types (the high water mark).

![High water mark example: three information types rolling up to an overall moderate rating](/assets/images/castellan-high-water-mark.svg)

This calculation is a simple pure function (same inputs, same output) and is fully unit-tested. There's no judgment call hidden in it.

**Select.** The system's high water mark determines which NIST 800-53 baseline is used (149 controls for low, 287 for moderate, 370 for high). Castellan doesn't rely on hardcoded lists. Instead, it downloads NIST's machine-readable catalog and baseline files (in NIST's own OSCAL JSON format) and dynamically determines the correct baseline from the source of truth. The NIST artifacts are downloaded once and then cached locally, so the tool can run entirely offline thereafter. The idea here is to base every claim on the definitive artifact: a hardcoded list is a copy, and copies drift.

**Generate the SSP.** For a moderate system, Castellan outputs a skeletal plan that covers all 287 controls. It includes the control text, the owner, and a field for implementation status. The output is both in readable Markdown format and OSCAL JSON. The structure of the JSON file mimics NIST's own published examples. To avoid guesswork, when the JSON format was uncertain, I downloaded NIST's own example and replicated its structure exactly.

**Scan.** Twenty read-only checks inspect the host: SSH configuration (root login disabled? Weak ciphers banned?), account policy (passwords set to expire? Is any non-root account UID 0?), file permissions (/etc/shadow locked down? World-writable files in system directories?), services (auditd running? Firewall enabled?), logging, and automatic updates. Each check performs three things: it inspects a specific piece of the system, defines what constitutes success, and generates the command needed for remediation if it fails. Checks are unable to modify the host not merely because I wrote careful code, but because they access the system through a 5-method interface:

![The Host interface: checks on one side, LinuxHost and FakeHost implementations on the other](/assets/images/castellan-host-interface.svg)

The interface lacks any write methods, meaning that modifying the host is not just against the rules, it's structurally impossible. The interface also makes the scanner easily testable, since tests substitute a fake host, in-memory and constructed from fixture files, allowing 208 tests to be run against Windows, Linux, or a CI container without actually touching a real machine. Another important rule governing the runner: any check that throws an exception is treated as an error and its result is recorded, but the scan continues and the remaining 19 checks are still executed.

**Map.** This is the core component and intentionally the most boring file in the entire repository: a small hand-written table mapping each check to the controls it validates, accompanied by a one-line rationale.

![Sample rows from the mapping: check ids on the left, the controls they evidence on the right](/assets/images/castellan-mapping.svg)

This idea is officially known in the military space as Control Correlation Identifiers (CCIs); Castellan's table is a hand-curated analog of CCI, built for its own checks. Because this mapping is the part an assessor is most likely to attack, it is rigorously tested: every check must be mapped, every mapped control must exist in the real NIST catalog and the moderate baseline, and a renamed check with a stale mapping entry fails the build. Aquinas opens one of his treatises by warning that a small error in the beginning becomes a great one in the end. A mapping table is the beginning of every claim the report makes, so this is where the rigor went.

**Report.** The findings flow through the mapping and each control receives a status by a fixed rule.

![The status rules: check outcomes on the left mapping to control statuses on the right](/assets/images/castellan-status-rules.svg)

That last row is the rule I care most about. A host scan can verify twenty technical facts. It cannot verify whether you have an incident response plan, whether staff got security training, or whether visitors sign in at the server room. Most of the 287 controls are organizational like that. A tool that marked them green because nothing contradicted them would be committing rash judgment in Aquinas's exact sense: asserting beyond its evidence. So Castellan reports them as not assessed, plainly and in large numbers. The same principle governs the edge cases: a check that does not apply (no SSH server installed) says not applicable rather than pass, and a check that could not look (a file it lacked permission to read) says error rather than pretending it looked.

## The honest numbers

The repository ships with output from a real run against a real Ubuntu host, committed as is.

![The scorecard from the real run: 8 pass, 5 fail, 1 error, 6 not applicable; 11 of 287 controls assessable, 45.5 percent passing, 6 POA&M items](/assets/images/castellan-scorecard.svg)

The POA&M reads like a real one because it is one: the audit daemon was not running, no firewall was active, passwords were set to never expire, and `/etc/crontab` was readable by everyone. Each item names the failing check and the exact command that fixes it.

I want to dwell on why I published those numbers instead of staging a prettier host. Aquinas held that truth is the good of the intellect, the thing the mind is *for*. The analogous point here is that truth is the good of a report. A compliance report has exactly one source of value: that its claims conform to the machine. The moment it flatters, it is worthless, no matter how green the dashboard. A report that says 45.5% and lists six failures is more useful, and frankly more impressive to anyone who has done this work, than one that claims a hundred and proves nothing. The committed sample run, failures and all, is the tool demonstrating its own design principle.

## The map and the territory

Every technical choice in Castellan reduces to one idea. The document and the host are two descriptions of one system, and only one of them can be authoritative. The host is the *res*, the thing. The paperwork is the *intellectus*, the set of judgments. The tool's whole job is adequation: walking the walls, comparing the claims to the stones, and reporting the difference without flinching.

That is what a castellan was for. The lord did not need a flattering map of the fortress. He needed to know which gate would not hold.

*Castellan is MIT licensed and on [GitHub](https://github.com/mthompsen/castellan). The README has an architecture diagram, a quickstart, and the full sample evidence package.*
