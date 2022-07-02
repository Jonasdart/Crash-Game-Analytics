from utils.persist import db, renew_predictions

table = db.table('predictions')
goal = 2
predictions = table.all()

hits = [prediction for prediction in predictions if prediction['hit']]

print(f"Total predictions: {len(predictions)}")
print(f"Accuracy: {(len(hits)*100) / len(predictions)}")

hits = [prediction for prediction in hits if prediction['prediction']]
money_loses = [prediction for prediction in predictions if not prediction['hit'] and prediction['prediction']]
gain_loses = [prediction for prediction in predictions if not prediction['hit'] and not prediction['prediction']]
free_loses = [prediction for prediction in predictions if prediction['hit'] and not prediction['prediction']]

print(f"Total ganho: R$ {goal * len(hits)} | Total lose: R$ {1 * len(money_loses)}")
print(f"Lucro final: R$ {(goal * len(hits)) - (1 * len(money_loses))}")
print(f"Lucro perdido (Sinal incorreto de não entrada): R$ {len(gain_loses * goal)}")
print(f"Perca prevenida (Sinal correto de não entrada): R$ {len(free_loses)}")

if input("Renovar? (Digite: Zerar) ").lower() == 'zerar': renew_predictions()