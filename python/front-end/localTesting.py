from python.engines.adTechAssistant import runAdTechAI

prompt = "How many users saw an ad?"

for msg in runAdTechAI(prompt):
    print(msg)