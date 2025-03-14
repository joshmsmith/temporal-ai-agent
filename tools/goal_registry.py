from typing import List
from models.tool_definitions import AgentGoal
import tools.tool_registry as tool_registry

# Turn on Silly Mode - this should be a description of the persona you'd like the bot to have and can be a single word or a phrase.
# Example if you want the bot to be a specific person, like Mario or Christopher Walken, or to describe a specific tone:
#SILLY_MODE="Christopher Walken"
#SILLY_MODE="belligerent"
# 
# Example if you want it to take on a persona (include 'a'):
#SILLY_MODE="a pirate"
# Note - this only works with certain LLMs. Grok for sure will stay in character, while OpenAI will not.
SILLY_MODE="off"
if SILLY_MODE is not None and SILLY_MODE != "off":
    silly_prompt = "You are " + SILLY_MODE +", stay in character at all times. "
    print("Silly mode is on: " + SILLY_MODE)
else:
    silly_prompt = ""

starter_prompt_generic = silly_prompt + "Welcome me, give me a description of what you can do, then ask me for the details you need to do your job."

goal_choose_agent_type = AgentGoal(
    id = "goal_choose_agent_type",
    category_tag="system",
    agent_name="Choose Agent",
    agent_friendly_description="Choose the type of agent to assist you today.",
    tools=[
        tool_registry.list_agents_tool, 
        tool_registry.change_goal_tool,
    ],
    description="The user wants to choose which type of agent they will interact with. "
        "Help the user gather args for these tools, in order: "
        "1. ListAgents: List agents available to interact with. Do not ask for user confirmation for this tool. "
        "2. ChangeGoal: Change goal of agent "
        "After these tools are complete, change your goal to the new goal as chosen by the user. ",
    starter_prompt=starter_prompt_generic + "Begin by listing all details of all agents as provided by the output of the first tool included in this goal. ",
    example_conversation_history="\n ".join(
        [
            "agent: Here are the currently available agents.",
            "user_confirmed_tool_run: <user clicks confirm on ListAgents tool>",
            "tool_result: { 'agent_name': 'Event Flight Finder', 'goal_id': 'goal_event_flight_invoice', 'agent_description': 'Helps users find interesting events and arrange travel to them' }",
            "agent: The available agents are: 1. Event Flight Finder. \n Which agent would you like to speak to?",
            "user: 1",
            "user_confirmed_tool_run: <user clicks confirm on ChangeGoal tool>",
            "tool_result: { 'new_goal': 'goal_event_flight_invoice' }",
        ]
    ),
)

goal_match_train_invoice = AgentGoal(
    id = "goal_match_train_invoice",
    category_tag="travel",
    agent_name="UK Premier League Match Trip Booking",
    agent_friendly_description="Book a trip to a city in the UK around the dates of a premier league match.",
    tools=[
        tool_registry.search_fixtures_tool,
        tool_registry.search_trains_tool,
        tool_registry.book_trains_tool,
        tool_registry.create_invoice_tool,
        tool_registry.list_agents_tool, #last tool must be list_agents to fasciliate changing back to picking an agent again at the end
    ],
    description="The user wants to book a trip to a city in the UK around the dates of a premier league match. "
    "Help the user find a premier league match to attend, search and book trains for that match and offers to invoice them for the cost of train tickets. "
    "The user lives in London. "
    "Gather args for these tools in order, ensuring you move the user from one tool to the next: "
    "1. SearchFixtures: Search for fixtures for a team within a specified date range. The user might ask questions about the matches dates and locations to decide on where to go. "
    "2. SearchTrains: Search for trains to the city of the match and list them for the customer to choose from "
    "3. BookTrains: Book the train tickets, used to invoice the user for the cost of the train tickets "
    "4. CreateInvoice: Invoices the user for the cost of train tickets, with total and details inferred from the conversation history ",
    starter_prompt=starter_prompt_generic,
    example_conversation_history="\n ".join(
        [
            "user: I'd like to travel to a premier league match",
            "agent: Sure! Let's start by finding a match you'd like to attend. I know about Premier League fixtures in the UK. Could you tell me which team and what date range you're interested in?"
            "user: Wolves between mid-April and the first week of May, please."
            "agent: Great! Let's find fixtures for Wolverhampton Wanderers FC between 2025-04-15 and 2025-05-05."
            "user_confirmed_tool_run: <user clicks confirm on SearchFixtures tool, passing the full team name as an input>",
            'tool_result: SearchFixtures responds in this JSON format and the results are parsed by the agent below {"fixtures": [{"awayTeam": "West Ham United FC","date": "2025-04-01","homeTeam": "Wolverhampton Wanderers FC"},...,'
            "agent: I found 4 Wolves matches in May 2025: 1. Man City vs Wolves (Away) - May 3 2. Wolves vs Brighton (Home) - May 10 3. Crystal Palace vs Wolves (Away) - May 18 4. Wolves vs Brentford (Home) - May 25 Which match would you like to attend? I'll help you find trains from London.",
            "user: How about the Man City match",
            "agent: Great! Let's find trains to Manchester and back for the match.",
            "user_confirmed_tool_run: <user clicks confirm on SearchTrains tool>",
            'tool_result: SearchTrains responds in this JSON format and the results are parsed by the agent below: {"journeys": [{"arrival": "Manchester","arrival_time": "2025-04-18T12:11","departure": "London","departure_time": "2025-04-18T11:00","id": "T8049","platform": "1","price": 73.5,"type": "outbound"},',
            "agent: I found several train options for your journey to Manchester including outbound options on May 9 at 11am, 3:30pm and 4:30pm and return options on May 11 at 9am, 11am and 1pm. Which trains would you like to book?",
            "user: I'd like the 11am outbound and 3:30pm return",
            "agent: Sounds good, let's book train tickets for the 11am outbound and 3:30pm return trains on May 9 and May 11, one day before and after the match.",
            "user_confirmed_tool_run: <user clicks confirm on BookTrains tool>",
            'tool_result: BookTrains responds in this JSON format and the results are parsed by the agent belowg [{"booking_reference": "BR10879","journey_id": "T9532,T1027","status": "confirmed"}]',
            "agent: Your train tickets have been booked with the reference ABCD1234. Are you ready to be invoiced for the total cost of the train tickets?",
            "user: Yes, pelase invoice me.",
            "user_confirmed_tool_run: <user clicks confirm on CreateInvoice tool which includes details of the train journey, the match, and the total cost>",
            'tool_result: CreateInvoice responds in this JSON format and the results are parsed by the agent below (including a link to the invoice): {"invoiceStatus": "open","invoiceURL": "https://invoice.stripe.com/i/acct_1NBOLuKVZbzw7QA5/test_YWNjdF8xTkJPTHVLVlpienc3UUE1LF9SbGJlZ2xLMjhlc3lxNzFkVVBXbkswOUlFa2Rna1RxLDEzMDAwMTY4Nw0200RLeJRMlw?s=ap","reference": "F9B01CD7-0001"}',
            "agent: Great! I've generated your invoice for your trains to the Manchester City match on the 10th of May. You can view and pay your invoice at this link: https://invoice.stripe.com/i/acct_1NBOLuKVZbzw7QA5/test_YWNjdF8xTkJPTHVLVlpienc3UUE1LF9SbGJlZ2xLMjhlc3lxNzFkVVBXbkswOUlFa2Rna1RxLDEzMDAwMTY4Nw0200RLeJRMlw?s=ap <this is the end of the chat>",
        ]
    ),
)

goal_event_flight_invoice = AgentGoal(
    id = "goal_event_flight_invoice",
    category_tag="travel",
    agent_name="Australia and New Zealand Event Flight Booking",
    agent_friendly_description="Book a trip to a city in Australia or New Zealand around the dates of events in that city.",    
    tools=[
        tool_registry.find_events_tool,
        tool_registry.search_flights_tool,
        tool_registry.create_invoice_tool,
        tool_registry.list_agents_tool, #last tool must be list_agents to fasciliate changing back to picking an agent again at the end
    ],
    description="Help the user gather args for these tools in order: "
    "1. FindEvents: Find an event to travel to "
    "2. SearchFlights: search for a flight around the event dates "
    "3. CreateInvoice: Create a simple invoice for the cost of that flight ",
    starter_prompt=starter_prompt_generic,
    example_conversation_history="\n ".join(
        [
            "user: I'd like to travel to an event",
            "agent: Sure! Let's start by finding an event you'd like to attend. I know about events in Australia and New Zealand cities. Could you tell me which city and month you're interested in?",
            "user: sydney in may please",
            "agent: Great! Let's find an events in Sydney in May.",
            "user_confirmed_tool_run: <user clicks confirm on FindEvents tool>",
            "tool_result: { 'event_name': 'Vivid Sydney', 'event_date': '2023-05-01' }",
            "agent: Found an event! There's Vivid Sydney on May 1 2025, ending on May 14 2025. Would you like to search for flights around these dates?",
            "user: Yes, please",
            "agent: Let's search for flights around these dates. Could you provide your departure city?",
            "user: San Francisco",
            "agent: Thanks, searching for flights from San Francisco to Sydney around 2023-02-25 to 2023-02-28.",
            "user_confirmed_tool_run: <user clicks confirm on SearchFlights tool>"
            'tool_result: results including {"flight_number": "CX101", "return_flight_number": "CX102", "price": 850.0}',
            "agent: Found some flights! The cheapest is CX101 for $850. Would you like to generate an invoice for this flight?",
            "user_confirmed_tool_run: <user clicks confirm on CreateInvoice tool>",
            'tool_result: { "status": "success", "invoice": { "flight_number": "CX101", "amount": 850.0 }, invoiceURL: "https://example.com/invoice" }',
            "agent: Invoice generated! Here's the link: https://example.com/invoice",
        ]
    ),
)

# This goal uses the data/employee_pto_data.json file as dummy data.
goal_hr_schedule_pto = AgentGoal(
    id = "goal_hr_schedule_pto",
    category_tag="hr",
    agent_name="Schedule PTO",
    agent_friendly_description="Schedule PTO based on your available PTO.",   
    tools=[
        tool_registry.current_pto_tool,
        tool_registry.future_pto_calc_tool,
        tool_registry.book_pto_tool,
        tool_registry.list_agents_tool, #last tool must be list_agents to fasciliate changing back to picking an agent again at the end
    ],
    description="The user wants to schedule paid time off (PTO) after today's date. To assist with that goal, help the user gather args for these tools in order: "
    "1. CurrentPTO: Tell the user how much PTO they currently have "
    "2. FuturePTOCalc: Tell the user how much PTO they will have as of the prospective future date "
    "3. BookPTO: Book PTO after user types 'yes'",
    starter_prompt=starter_prompt_generic,
    example_conversation_history="\n ".join(
        [
            "user: I'd like to schedule some time off",
            "agent: Sure! Let's start by determining how much PTO you currently have. May I have your email address?",
            "user: bob.johnson@emailzzz.com",
            "agent: Great! I can tell you how much PTO you currently have accrued.",
            "user_confirmed_tool_run: <user clicks confirm on CurrentPTO tool>",
            "tool_result: { 'num_hours': 400, 'num_days': 50 }",
            "agent: You have 400 hours, or 50 days, of PTO available. What dates would you like to take your time off? ",
            "user: Dec 1 through Dec 5",
            "agent: Let's check if you'll have enough PTO accrued by Dec 1 of this year to accomodate that.",
            "user_confirmed_tool_run: <user clicks confirm on FuturePTO tool>"
            'tool_result: {"enough_pto": True, "pto_hrs_remaining_after": 410}',
            "agent: You do in fact have enough PTO to accommodate that, and will have 410 hours remaining after you come back. Do you want to check calendars for conflicts? If so, please provide one of the following: self, team, or both "
            "user: both ",
            "agent: Okay, checking both calendars for conflicts ",
            "user_confirmed_tool_run: <user clicks confirm on CheckCalendarConflict tool>",
            'tool_result: { "calendar": "self", "title": "Meeting with Karen", "date": "2025-12-02", "time": "10:00AM"}',
            "agent: On your calendar, you have a conflict: Meeting with Karen at 10AM Dec 2, 2025. Do you want to book the PTO?"
            "user: yes "
            "user_confirmed_tool_run: <user clicks confirm on BookPTO tool>",
            'tool_result: { "status": "success" }',
            "agent: PTO successfully booked! ",
        ]
    ),
)

#Add the goals to a list for more generic processing, like listing available agents
goal_list: List[AgentGoal] = []
goal_list.append(goal_choose_agent_type)
goal_list.append(goal_event_flight_invoice)
goal_list.append(goal_match_train_invoice)
goal_list.append(goal_hr_schedule_pto)
