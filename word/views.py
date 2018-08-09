from django.shortcuts import render, redirect

from .forms import WordForm

from gensim.models import word2vec
from gensim.models.keyedvectors import KeyedVectors

from collections import defaultdict

# Create your views here.
file_path = "../../Data/tansaku_meishi.model"
#file_path = "../../Data/tansaku.model"
#word_model = word2vec.Word2Vec.load(file_path)
#keyed_model = KeyedVectors.load(file_path)

def load_model():
    global word_model
    word_model = word2vec.Word2Vec.load(file_path)
    global keyed_model
    keyed_model = KeyedVectors.load(file_path)

load_model()

from sklearn.cluster import KMeans
def make_cluster():
    vocab = list(keyed_model.wv.vocab.keys())[:3000]
    vectors = [keyed_model.wv[word] for word in vocab]
    n_clusters = 15
    kmeans_model = KMeans(n_clusters=n_clusters, verbose=1, random_state=42, n_jobs=-1)
    kmeans_model.fit(vectors)

    cluster_labels = kmeans_model.labels_

    cluster_to_words = defaultdict(list)
    for cluster_id, word in zip(cluster_labels, vocab):
        cluster_to_words[cluster_id].append(word)
    
    global cluster
    cluster = cluster_to_words

make_cluster()

def portal(request):

    if request.method=="POST":
      form = WordForm(request.POST)
      if form.is_valid():
        similars = get_word_table(form.cleaned_data['word'])
        clusters = get_cluster_table(form.cleaned_data['word'])

    else:
      if "word_param" in request.GET:
          word = request.GET.get('word_param')
          similars = get_word_table(word)
          clusters = get_cluster_table(word)
          form = WordForm(initial={'word': word}) 
      else:
          form = WordForm()
          similars = []
          clusters = []

    return render(request, 'word/portal.html', {'form': form, 'similars': similars, 'clusters': clusters})


def rebuild_model(request):
    load_model()
    make_cluster()

    return redirect('word_portal')


def get_word_table(word):
    try:
        ret = []
        res = word_model.wv.most_similar(positive=[word])
        print("similars")
        for result in res:
            print(result)
            print(result[0])
            print(word_model.wv.vocab[result[0]])
            ret.append([result[0], round(result[1], 5), word_model.wv.vocab[result[0]].count])

        print(ret)
        return ret
    except KeyError:
        print(f"word {word} not in vocablary")
        #res = [(f"word [{word}] not in vocablafy")]
        res = []

    return res

def count_vocab(word):
  return word_model.wv.vocab[word].count

def get_cluster_table(word):
    for words in cluster.values():
        if word in words:
            res = []
            for w in words:
                res.append([w, count_vocab(w)])
            print(words)
            return res
    return []


