# deep-wifi-project
A project aims at solving issues and improving the performance of wifi based on deep learning

### Requirements
- python 3+
- [jupyter](http://jupyter.org/)
- [networkx](https://github.com/networkx/networkx)

### Getting Started
```bash
# it's better to use any kind of virtual env
pip3 install -r requirements.txt

# install core packages if using anaconda
conda install networkx matplotlib numpy jupyter theano lasagne
```

## Usage

### Events (aggregated with counts, apids)
- bar chart
- stacked bar chart
```bash
cd draw_client_route
python router_events.py # there should be a file called router_events.log generated

jupyter notebook # navigate to routers.ipynb and all to see the resulted charts
```

## Resources

### Good Deep Learning Basic Tutorial
- http://neuralnetworksanddeeplearning.com/chap1.html
- http://colah.github.io/

### Lasagne and Keras Tutorial
- http://lasagne.readthedocs.io/en/latest/
- https://keras.io/

### Good RNN materials
- https://www.nervanasys.com/intern-spotlight-implementing-language-models/
- http://www.wildml.com/2015/09/recurrent-neural-networks-tutorial-part-2-implementing-a-language-model-rnn-with-python-numpy-and-theano/

### Machine Learning
- http://scikit-learn.org/
- http://scikit-image.org/
