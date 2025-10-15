# Helios Protocol - Automated Rollback and Postmortem System

## Overview

The Helios Protocol is an automated deployment safety system that monitors all phases of deployment and automatically triggers rollbacks when NO-GO decisions are detected. It enforces mandatory postmortem completion before allowing new deployments.

## Key Features

### 1. **Automatic Rollback on NO-GO**
- Monitors all deployment phases (Pre-deployment, Deployment, Post-deployment, Verification, Monitoring)
- Immediately deploys last known stable version on any NO-GO decision
- Thread-safe rollback execution
- Integration with existing patch manager

### 2. **Mandatory Postmortem Process**
- Automatically creates Severity-1 postmortem tasks on rollback
- Blocks all new deployments until postmortem is completed
- Requires root cause analysis and corrective actions
- Maintains complete audit trail

### 3. **Multi-Agent Coordination**
- Prevents duplicate operations across multiple agents
- Coordinates rollback actions
- Ensures agents work in unison
- Task assignment and tracking

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Helios Protocol                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │   Phase     │  │   Rollback   │  │  Postmortem   │ │
│  │ Monitoring  │  │   Engine     │  │   Manager     │ │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘ │
│         │                 │                   │         │
│  ┌──────▼─────────────────▼───────────────────▼──────┐ │
│  │              Helios Database                       │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │            Helios Coordinator                      │ │
│  │  - Agent Registration                              │ │
│  │  - Task Deduplication                              │ │
│  │  - Operation Coordination                          │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Usage

### Command Line Interface

```bash
# Check system status
./helios status

# List open postmortems
./helios postmortems list --open-only

# View specific postmortem
./helios postmortems view PM-deploy_12345-abc123

# Complete a postmortem
./helios postmortems complete PM-deploy_12345-abc123 "Database connection leak" \
  --actions-file corrective_actions.txt

# View rollback history
./helios rollbacks

# Mark version as stable
./helios mark-stable backup_1234567890
```

### Python Integration

```python
from helios.helios_protocol import helios_protocol, HeliosPhase, DecisionStatus

# Check if deployments are allowed
can_deploy, message = helios_protocol.can_deploy()

# Register a deployment
if can_deploy:
    helios_protocol.register_deployment("deploy_123", "1.0.0", "Feature X deployment")

# Record phase decisions
helios_protocol.record_phase_decision(
    HeliosPhase.PRE_DEPLOYMENT,
    DecisionStatus.GO,
    "All pre-deployment checks passed"
)

# NO-GO triggers automatic rollback
helios_protocol.record_phase_decision(
    HeliosPhase.VERIFICATION,
    DecisionStatus.NO_GO,
    "Memory usage exceeds threshold"
)
```

### Multi-Agent Coordination

```python
from helios.helios_coordinator import create_coordinator

# Create coordinator
coordinator = create_coordinator(helios_protocol)

# Register agent
coordinator.register_agent("agent_1")

# Request deployment action (prevents duplicates)
result = coordinator.request_deployment_action(
    "agent_1", 
    "deploy_123", 
    "deploy"
)

if result['allowed']:
    # Perform deployment
    pass
```

## Deployment Phases

1. **PRE_DEPLOYMENT**: System checks before deployment
2. **DEPLOYMENT**: Active deployment process
3. **POST_DEPLOYMENT**: Initial verification after deployment
4. **VERIFICATION**: Extended verification period
5. **MONITORING**: Ongoing system monitoring

## Postmortem Severity Levels

- **Severity 1**: Critical - Blocks all deployments
- **Severity 2**: High - Should be resolved soon
- **Severity 3**: Medium - Can be scheduled
- **Severity 4**: Low - Informational

## Database Schema

The Helios Protocol maintains the following tables:
- `deployments`: Deployment records
- `phase_decisions`: Phase GO/NO-GO decisions
- `postmortems`: Postmortem tasks and completion
- `rollback_history`: Rollback audit trail
- `stable_versions`: Known stable versions

## Testing

Run the comprehensive test suite:

```bash
python3 modules/helios/test_helios.py
```

## Integration with TPS19

The Helios Protocol is fully integrated into the TPS19 main system:
- Automatic deployment registration on startup
- Phase decision recording throughout operation
- Error threshold monitoring
- Automatic rollback on critical errors
- Clean shutdown handling

## Best Practices

1. **Always Complete Postmortems**: System deployments remain blocked until Severity-1 postmortems are resolved
2. **Mark Stable Versions**: Regularly mark known-good versions as stable for rollback targets
3. **Monitor Phase Decisions**: Review phase decisions to identify patterns
4. **Test Rollbacks**: Regularly test rollback procedures in non-production environments

## Troubleshooting

### Deployments Blocked
```bash
# Check status
./helios status

# List open postmortems
./helios postmortems list --open-only

# Complete required postmortems
./helios postmortems complete <ID> "<root cause>"
```

### Failed Rollback
- Check patch manager logs
- Verify backup exists
- Ensure stable version is marked
- Review rollback history: `./helios rollbacks`

### Agent Coordination Issues
- Ensure agents have unique IDs
- Check coordinator status in logs
- Verify task assignments
- Review coordination logs

## Security Considerations

- Postmortem completion requires proper authorization
- Rollback operations are logged for audit
- Database access should be restricted
- Regular backups of Helios database recommended