import autogen
import os
from typing import Dict

class AutoGenRetryLoop:
    def __init__(self, llm_config: Dict):
        self.llm_config = llm_config

    def run_debate(self, plan: str, test_failure: str):
        """Runs a debate between a Planner and a Tester to refine the fix."""
        
        planner = autogen.AssistantAgent(
            name="Planner",
            llm_config=self.llm_config,
            system_message="You are the Lead Planner. You refine the bug-fix strategy based on test failures."
        )

        tester = autogen.AssistantAgent(
            name="Tester",
            llm_config=self.llm_config,
            system_message="You are the Critic. You analyze why the test failed and challenge the Planner's strategy."
        )

        user_proxy = autogen.UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
            is_termination_msg=lambda x: "FIX_READY" in x.get("content", "")
        )

        debate_prompt = f"""
        Original Plan: {plan}
        Test Failure: {test_failure}
        
        Planner and Tester, please debate the cause of this failure and suggest a refined strategy.
        When you agree on a new plan, end the message with 'FIX_READY'.
        """

        groupchat = autogen.GroupChat(agents=[user_proxy, planner, tester], messages=[], max_round=6)
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=self.llm_config)

        user_proxy.initiate_chat(manager, message=debate_prompt)
        
        # Return the last message as the refined plan
        return groupchat.messages[-1]["content"]
