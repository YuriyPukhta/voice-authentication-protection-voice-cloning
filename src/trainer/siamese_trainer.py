import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from tqdm import tqdm


def evaluate_siamese_model(model, dataloader, criterion, device='cpu'):
    model.eval()
    total_loss = 0.0
    predictions = []
    true_labels = []

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating", leave=False):
            anchor_sgram, posneg_sgram, label = batch
            anchor_sgram = anchor_sgram.to(device)
            posneg_sgram = posneg_sgram.to(device)
            label = label.to(device)
            output = model(anchor_sgram, posneg_sgram)
            loss = criterion(output, label)
            total_loss += loss.item()

            predictions += [torch.argmax(pred) for pred in output.cpu()]
            true_labels += [label.item() for label in label.cpu()]

    accuracy = accuracy_score(true_labels, predictions)
    precision = precision_score(true_labels, predictions)
    recall = recall_score(true_labels, predictions)
    f1 = f1_score(true_labels, predictions)

    avg_loss = total_loss / len(dataloader)

    return avg_loss, accuracy, precision, recall, f1


def train_siamese_model(model, dataloader, criterion, optimizer, device='cpu'):
    model.train()
    total_loss = 0.0
    predictions = []
    true_labels = []

    for batch in tqdm(dataloader, desc="Training", leave=False):
        anchor_sgram, posneg_sgram, label = batch
        anchor_sgram = anchor_sgram.to(device)
        posneg_sgram = posneg_sgram.to(device)
        label = label.to(device)

        optimizer.zero_grad()
        output = model(anchor_sgram, posneg_sgram)
        loss = criterion(output, label)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        predictions += [torch.argmax(pred) for pred in output.cpu()]
        true_labels += [label.item() for label in label.cpu()]

    accuracy = accuracy_score(true_labels, predictions)
    precision = precision_score(true_labels, predictions)
    recall = recall_score(true_labels, predictions)
    f1 = f1_score(true_labels, predictions)

    avg_loss = total_loss / len(dataloader)
    avg_loss = total_loss / len(dataloader)

    return avg_loss, accuracy, precision, recall, f1


def fit(model, train_dl, test_dl, criterion, optimizer, device, num_epochs=10):
    loss, accuracy, precision, recall, f1 = [], [], [], [], []
    for epoch in range(num_epochs):
        _train_loss, _train_accuracy, _train_precision, _train_recall, _train_f1 = train_siamese_model(
            model, train_dl, criterion, optimizer, device)
        print(f"Epoch train{epoch + 1}/{num_epochs}, Loss: {_train_loss:.4f}, "f"Accuracy: {_train_accuracy:.4f}, Precision: {_train_precision:.4f}, Recall: {_train_recall:.4f}, F1: {_train_f1:.4f}")
        _test_loss, _test_accuracy, _test_precision, _test_recall, _test_f1 = evaluate(
            model, test_dl, criterion, device)
        print(f"Epoch test{epoch + 1}/{num_epochs}, Loss: {_test_loss:.4f}, "f"Accuracy: {_test_accuracy:.4f}, Precision: {_test_precision:.4f}, Recall: {_test_recall:.4f}, F1: {_test_f1:.4f}")
        loss.append([_train_loss, _test_loss])
        accuracy.append([_train_accuracy, _test_accuracy])
        precision.append([_train_precision, _test_precision])
        recall.append([_train_recall, _test_recall])
        f1.append([_train_f1, _test_f1])

    return loss, accuracy, precision, recall, f1
