# Original prompt — First_agent_template

*The request that started this agent, verbatim (22 Nov 2026). The plan it produced, after two adversarial reviews: [PLAN.md](PLAN.md).*

```text
Claudio bellezza sei o non sei il top del top e ti pago profumatamente? le montiamo tutte. 

/plan minimal fix to app.py of https://huggingface.co/spaces/MArcoMondelloMBAMArch/First_Agent_Template to create each of the 5 tools proposed.
 Add Cross check how many units and bonus units the course has and create a new tool course_coverage() as a percentage that grows with my progresses (units 1 to 4: up to 80%, bonus units remaining 20%).
Add a tool to count the experiments. The tools must live in the space and be documented in the git repo wihtout cloning the app. 
The ideal  location is a new folder properly called (/my_agents); evaluate notebook with link to the actual space and the diff, if there is no more elegant way to do it. 
Test your work before declaring it done, loop until you are satisfied in your role of high school professor: it must be excellent but not perfect, simple, not overengineered. 
The ultimate goal is to have the answer questions like "how to set the .env" answered by everyone. 
Make sure this agent is scalable as my repo grows without maintenance. Make sure my privacy and security in general are top concern. Change system prompt if necessary. 
Implement a signature {closing} : 
"<repo-name> by <me> as of <datetime> (Berlin, CEST) covers <course_coverage>, synthesized <count_brain_notes> and <count_experiments>, and has <stars> in Github. Looking forward to yours! 
Present me the plan only after an adversarial review. Split the work in work package and parallelize to agents as much as you can. 
Keep the calls to my HF credit usage to the bare minimum, eventually changing the main agent if laggy or buggy. 
The app and the repo must end up in my portfolio as an entry frontend deployed engineer.
```

## Clarifications given while planning

- The agent answers **any** question, not only about the `.env`: questions about what I learned are answered from my notes, the rest normally.
- Layout: `my-agents/<Agent>/` holds only the original prompt, the plan and a notebook (link to the Space + the diff explained); an index `my-agents/ROASTER.md` lists the agents. The code lives **only** in the Space.
- Cost: I pay for anonymous visitors, **25 questions/day in total**; with "Sign in with Hugging Face" the visitor pays, **20/day per username**.
- `course_coverage()`: rule "moved on" (a unit is done when notes for a later chapter exist; the current unit counts half).
- Privacy: the Space is linked openly from this repo: it is my portfolio.
- Working mode: autonomous until done; stop only for safety, privacy, incomprehension or unexpected issues.
