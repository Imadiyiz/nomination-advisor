# Architecture

## 1. Purpose

The Architecture document is responsible for enabling future developers or myself to understand
how the different systems within the project interact with each other.

## 2. Architectural Principles

- GameState is the source of truth
- State transitions produce new GameState objects
- BotPlayer is responsible for CPU decision-making
- HumanPlayer is responsible for Human decision-making
- RolloutSimulator is responsible for simulation and does not take player input
- BeliefModel represents incomplete information

## 3. System Overview

[High-level Mermaid diagram]

Short explanation of each major component.

## 4. Game State

### Responsibilities

### State transitions

[State transition diagram]

### Invariants

Things that must always be true.

## 5. Bot Decision Making

### Responsibilities

### Decision flow

[Sequence diagram]

### Relationship with GameState

Explain what information is passed to the bot and what the bot is
allowed to modify.

## 6. Monte Carlo Simulation

### Rollout process

[Sequence diagram]

### World sampling

[BeliefModel diagram]

## 7. Component Responsibilities

| Component | Responsibility | Should NOT be responsible for |
|---|---|---|
| GameState | Represent game state | Deciding what a bot should play |
| BotPlayer | Choose actions | Mutating GameState |
| RolloutSimulator | Run hypothetical games | Implementing bot strategy |
| BeliefModel | Model hidden information | Applying game rules |
| Heuristics | Define behavioural preferences | Managing game state |

## 8. Important Invariants

Things that must remain true when modifying the software.

## 9. Extension Points

How a future developer should add:
- new bot strategies
- new heuristics
- different sampling techniques
- etc.

## 10. Known Limitations

Document deliberate simplifications and technical debt.