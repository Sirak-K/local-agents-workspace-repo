# WF-1-A — Prompting

Node 74 `REFERENCE IMAGE POSITIVE PROMPT - TEMPLATE` owns the complete positive prompt in both variants. Story Creator's Lumimaid Prompt-Realized pass writes its complete model-facing English text automatically before workflow application.

Required order:

`framing → subject count and description → pose/action → required visible details → clothing/objects → camera/composition → environment/background → lighting → materials/texture/finish`

Keep the result to one coherent present moment. Remove unused clauses instead of leaving empty placeholders or accumulating generic quality tokens.

The prompt begins with the human subject and exact visible action. It contains concrete visual values rather than plot summaries, future actions, abstract continuity categories or Story Creator terminology. When source material leaves presentation open, Prompt-Realized selects compatible framing, camera, lighting and finish without inventing characters, plot events or props.

## Primary FLUX.2 Dev

Node 74 routes through Node 78 `FluxGuidance(4)` to Node 63 `BasicGuider`. FLUX.2 receives a direct positive description; exclusions are expressed as the intended visible state because no negative-conditioning branch exists.

## Secondary Klein 9B Base

Node 74 provides positive conditioning. Node 76 is an active, intentionally empty negative prompt routed to Node 63 `CFGGuider`. Empty negative text is a deliberate model contract, not an unfilled placeholder.

The variants have different conditioning contracts. Do not copy Dev guidance or Klein negative-routing between them.
