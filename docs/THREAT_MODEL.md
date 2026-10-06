# Threat Model & Privacy Risk Matrix (fictional social-media user)

| Asset | Threat | Exposure | Potential impact | Existing control | Recommended control |
|---|---|---|---|---|---|
| Account | Account takeover | No MFA, reused password, no login alerts | Loss of messages/contacts, impersonation | Password | MFA, unique passwords + manager, login alerts |
| Identity information | Impersonation | Public birthday, photos, workplace | Fake profiles, fraud attempts | Profile settings | Limit public identity details; report fake profiles |
| Contact information | Phishing / unwanted contact | Public phone and email | Spam, targeted phishing | Visibility setting | Hide phone/email; separate public contact address |
| Location privacy | Unwanted profiling / physical safety | Real-time location, check-ins, routines | Safety risk while away | Geotag toggle | Disable live sharing; post after leaving; strip EXIF |
| Private content | Oversharing / exposure via others | Public posts, old posts, tagged photos | Reputation, data exposure | Post audience | Friends-only default, tag review, clean-up of old posts |
| Social relationships | Social engineering | Unknown connections, visible friends list | Convincing scams using relationship context | Request settings | Verify requests, prune connections, hide friends list |
| Linked accounts | Third-party app exposure | Old integrations, broad permissions | Data access by forgotten apps | App list | Least privilege; review/revoke apps regularly |

## Privacy Risk Matrix (educational; real risk depends on context)
| Item | Likelihood | Impact |
|---|---|---|
| Public phone number | Medium | Medium |
| Public full birthday | Medium | Medium |
| Real-time location exposure | Medium | High |
| MFA disabled | Medium | High |
| Password reuse | Medium | High |
| Unknown connections accepted | High | Medium |
| Tag review disabled | Medium | Low |
| Unreviewed third-party apps | Medium | Medium |
| Sharing verification codes | Low | High |
| Old posts unreviewed | Medium | Low |

## How oversharing can increase social-engineering risk (defensive view)
Scammers value *context*. Employer, college, travel dates, family references, interests and public events can make a fraudulent message feel legitimate. Defences: share less publicly, verify unusual requests through a second channel, never share OTPs, and treat urgency as a warning sign. This project deliberately contains no attack message templates.
