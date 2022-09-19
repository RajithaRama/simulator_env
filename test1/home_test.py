from Models.home import Home

patient_1_path = []

# Patient 1 path
# start
patient_1_path.append((6, 5))

# Move to couch in common area
patient_1_path.extend([(7, 5), (7, 4), (7, 3), (8, 3), (8, 2)])

# wait in couch for 60 secs
for i in range(30):
    patient_1_path.append((8, 2))

# move to Kitchen
patient_1_path.extend([(8, 2), (8, 3), (7, 3), (7, 4), (7, 5), (6, 5), (5, 5), (5, 4), (5, 3), (4, 3), (3, 3), (3, 2),
                       (2, 2)])

# wait in kitchen chair for 15 secs
for i in range(15):
    patient_1_path.append((2, 2))


#Patient 2 path

patient_2_path = []
for i in range(15):
    patient_2_path.append((9, 2))

model = Home(2, [patient_1_path[0], (9, 2)], (5, 7), [patient_1_path, patient_2_path])
model.step()
model.visible_stakeholders(model.robot.pos, 3)
print(model.get_location((5, 6)))
print(model.get_location((5, 7)))
