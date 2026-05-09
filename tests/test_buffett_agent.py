from auto_invest.buffett_agent import BuffettAgentInput, BuffettStyleAgent


def test_buffett_agent_buy_rating_when_most_rules_pass():
    agent = BuffettStyleAgent()
    result = agent.evaluate(
        BuffettAgentInput(
            symbol="FPT",
            current_price=60,
            eps=6,
            book_value_per_share=50,
            roe=0.2,
            debt_to_equity=0.3,
        )
    )
    assert result["rating"] == "BUY"
    assert result["score"] >= 4
