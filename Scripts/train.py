from ultralytics import YOLO

if __name__ == "__main__":

    # Create a new YOLO model from scratch
    model = YOLO("yolov5n.pt")

    # Load a pretrained YOLO model (recommended for training)
    #model = YOLO("yolov11n.pt")

    # Train the model using the 'coco8.yaml' dataset for 3 epochs
    # results = model.train(data="coco8.yaml", epochs=3)
    results = model.train(
        data="datasets/drone_dataset.yaml", 
        epochs=100,
        imgsz=720,
        lr0=0.001,  # Initial learning rate
        batch=16,  # Batch size
        optimizer="Adam",  # Choose optimizer: SGD or AdamW
        #momentum=0.937,
        weight_decay=1.3142636082792856e-06,
        augment=True,
        dropout=0.13960522885895857
    )

    # Evaluate the model's performance on the validation set
    #results = model.val(data="./dataset.yaml")

    # Perform object detection on an image using the model
    #results = model.predict(source='dataset/images/test', save=True)
    #dw = model("https://ultralytics.com/images/bus.jpg")

    # Export the model to ONNX format
    success = model.export(format="onnx")