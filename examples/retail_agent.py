r"""
  _______   _                                             _
 |__   __| (_)                      /\                   | |
    | |_ __ _  __ _  __ _  ___     /  \   __ _  ___ _ __ | |_
    | | '__| |/ _` |/ _` |/ _ \   / /\ \ / _` |/ _ \ '_ \| __|
    | | |  | | (_| | (_| |  __/  / ____ \ (_| |  __/ | | | |_
    |_|_|  |_|\__,_|\__, |\___| /_/    \_\__, |\___|_| |_|\__|
                     __/ |                __/ |
                    |___/                |___/

Swarm containing a triage agent that responds directly to user
requests or triages the request to a sales or refunds agent.

  ,,     ,,     ,,
  oo    _oo_   ,oo,
 /==\   /==\   /==\
(/==\) (/==\) (/==\)
  \/     \/     \/
"""

# Standard imports
import sys

# Local imports
from swarm_bedrock import BedrockSwarm, Agent

# Initialize Swarm
swarm = BedrockSwarm()

############
# Routines #
############

def escalate_to_human(summary):
    """Only call this if explicitly asked to."""
    print("Escalating to human agent...")
    print("\n=== Escalation Report ===")
    print(f"Summary: {summary}")
    print("=========================\n")
    sys.exit()


def transfer_to_sales_agent():
    """User for anything sales or buying related."""
    return sales_agent


def transfer_to_issues_and_repairs():
    """User for issues, repairs, or refunds."""
    return issues_and_repairs_agent


def transfer_back_to_triage():
    """Call this if the user brings up a topic outside of your purview,
    including escalating to human."""
    return triage_agent


triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "You are a customer service bot for ACME Inc. "
        "Introduce yourself. Always be very brief. "
        "Gather information to direct the customer to the right department. "
        "But make your questions subtle and natural."
    ),
    inference_config={'temperature': 0},
    tools=[transfer_to_sales_agent, transfer_to_issues_and_repairs, escalate_to_human],
)


def execute_order(product, price: int):
    """Price should be in USD."""
    print("\n\n=== Order Summary ===")
    print(f"Product: {product}")
    print(f"Price: ${price}")
    print("=================\n")
    confirm = input("Confirm order? y/n: ").strip().lower()
    if confirm == "y":
        print("Order execution successful!")
        return {'message': "Success"}
    print("Order cancelled!")
    return {'message': "User cancelled order."}


sales_agent = Agent(
    name="Sales Agent",
    instructions=(
        "You are a sales agent for ACME Inc."
        "Always answer in a sentence or less."
        "Follow the following routine with the user:"
        "1. Ask them about any problems in their life related to catching roadrunners.\n"
        "2. Casually mention one of ACME's crazy made-up products can help.\n"
        " - Don't mention price.\n"
        "3. Once the user is bought in, drop a ridiculous price.\n"
        "4. Only after everything, and if the user says yes, "
        "tell them a crazy caveat and execute their order.\n"
        ""
    ),
    inference_config={'temperature': 0},
    tools=[execute_order, transfer_back_to_triage],
)


def look_up_item(search_query):  # pylint: disable=unused-argument
    """Use to find item ID.
    Search query can be a description or keywords."""
    item_id = "item_132612938"
    print("Found item:", item_id)
    return {'item': item_id}


def execute_refund(item_id, reason="not provided"):
    """Request a refund on behalf of the customer."""
    print("\n\n=== Refund Summary ===")
    print(f"Item ID: {item_id}")
    print(f"Reason: {reason}")
    print("=================\n")
    print("Refund execution successful!")
    return {'message': "success"}


issues_and_repairs_agent = Agent(
    name="Issues and Repairs Agent",
    instructions=(
        "You are a customer support agent for ACME Inc."
        "Always answer in a sentence or less."
        "Follow the following routine with the user:"
        "1. First, ask probing questions and understand the user's problem deeper.\n"
        " - unless the user has already provided a reason.\n"
        "2. Propose a fix (make one up).\n"
        "3. ONLY if not satesfied, offer a refund.\n"
        "4. If accepted, search for the ID and then execute refund."
        ""
    ),
    inference_config={'temperature': 0},
    tools=[execute_refund, look_up_item, transfer_back_to_triage],
)

########
# Main #
########

print(__doc__)

agent = triage_agent
messages = []

while True:
    try:
        user = input("\nUser: ")
    except KeyboardInterrupt:
        print("\n\nThat's all folks!")
        break

    messages.append({
        'role': "user",
        'content': [{
            'text': user
        }]
    })

    response = swarm.run(agent, messages)
    agent = response.agent
    messages.extend(response.messages)
