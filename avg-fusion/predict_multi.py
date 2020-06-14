import tensorflow as tf
tf_config = tf.ConfigProto()
tf_config.gpu_options.allow_growth = True
tf.keras.backend.set_session(tf.Session(config=tf_config))

from tensorflow.python.keras.models import load_model
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, cohen_kappa_score
import configparser, argparse, datetime, json, os, visualize
import pandas as pd
from data_generator import test_crop_generator


networks = { 'resnet50': ['crop_resnet50' + x + '.h5' for x in ['2020-01-19 07:02:04']], # verified timestamp 1/7
            'densenet':['crop_densenet' + x + '.h5' for x in ['2020-01-19 13:59:12']],# verified timestamp 1/7
            'vgg16':['crop_vgg16' + x + '.h5' for x in ['2020-01-15 18:48:09']] # verified timestamp 1/7
}

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--configPath', help="""path to config file""", default='./config.ini')
parser.add_argument('-t', '--task', help="""classification task you are performing - either crop or energy""", default='crop-gad')
parser.add_argument('-n', '--network', help="""name of the network you are predicting for""", default='vgg16')
parser_args = parser.parse_args()

config = configparser.ConfigParser()
config.read(parser_args.configPath)
			
te_path = str(config[parser_args.task]['TEST_FOLDER'])

test_accuracies = []
for timestamp in networks[parser_args.network]:
    model_name = os.path.join('/mnt/data3/crop-classification/8_models/', timestamp)
    print(model_name)
    input_size = 224
    test_datagen = test_crop_generator(input_path=te_path, batch_size=1, mode="test", num_classes =6, epsilon = 0, resize_params = (224, 224), do_shuffle=True)

    print('Loading model {}'.format(model_name))

    model = load_model(model_name)

    all_predictions = []
    all_gt = []
    data_paths = []
    for te_data, label, curr_path in test_datagen:
        result = model.predict(te_data, verbose=0)
        #print(result.shape)
        prediction = np.argmax(result, axis = 1)
        #print(prediction, label)
        all_predictions.append(prediction)
        all_gt.append(label)
        data_paths.append(curr_path)
    #print(all_predictions)

    print(all_gt)

    cm = confusion_matrix(all_gt, all_predictions)

    print(cm)

    classes_lst = ['Corn', 'Cotton', 'Soy', 'Spring Wheat', 'Winter Wheat', 'Barley']

    creport = classification_report(y_true = all_gt, y_pred=all_predictions, target_names = classes_lst, digits = 4, output_dict = True)

    creport_df = pd.DataFrame(creport).transpose()

    acc = accuracy_score(all_gt, all_predictions)

    # f1 = f1_score(actual_labels, predictions, labels = classes_lst, average='samples')

    kappa_score = cohen_kappa_score(all_gt, all_predictions)

    print(creport)
    print('Accuracy for timestamp: {} is {}, kappa score = {}'.format(timestamp, acc, kappa_score))
    test_accuracies.append(acc)
    #for i in range(len(all_gt)):
    #    if all_predictions[i][0] != all_gt[i][0]:
    #        print('Path = {}, Actual = {}. Predicted = {}'.format(data_paths[i], all_gt[i][0], all_predictions[i][0]))
    visualize.plot_confusion_matrix(cm, classes=classes_lst, title=parser_args.network+'Avg Fusion Confusion Matrix')
    
print('All test accuracies = {}'.format(test_accuracies))
#visualize.plot_confusion_matrix(cm, classes=['Corn', 'Cotton', 'Soy', 'Wheat'], title=parser_args.network+' Confusion Matrix')

#creport_df.to_csv(parser_args.network+'creport.csv', index = True)
 
#for i in range(len(all_gt)):
#    if int(all_predictions[i]) != int(all_gt[i]):
#        print('Path = {}, Actual = {}. Predicted = {}'.format(data_paths[i], all_gt[i], all_predictions[i]))
        