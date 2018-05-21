# このscriptが存在するディレクトリで実行する必要があり
import sys
sys.path.append('../tutorial01')

import argparse
import math
from collections import defaultdict
from train_unigram import train_unigram


def arguments_parse():
    parser = argparse.ArgumentParser(
        usage='\t単語分割プログラム',
        description='説明',
        epilog='end',
        add_help=True,
    )
    parser.add_argument('-i', '--input', help='入力ファイル名', type=str)
    parser.add_argument('-t', '--train', help='学習用ファイル名', type=str)
    return parser.parse_args()


def split_words(test_file, train_file, unk_prob=0.05, vocab_num=1e6):
    '''単語分割して分割結果を my_answer.word に出力'''
    output_file = 'my_answer.word'

    # 学習
    train_unigram(train_file, 'trained.csv')

    # モデルの読み込み
    probs = defaultdict(float)
    for line in open('trained.csv', encoding='utf-8'):
        splited = line.split('\t')
        probs[splited[0]] = float(splited[1])

    # 出力ファイルを初期化
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in open(test_file, encoding='utf-8'):
            # 前向きステップ
            line = line.strip()
            best_edge = [0 for _ in range(len(line) + 1)]
            best_score = [0] + [sys.maxsize for _ in range(len(line))]
            for word_end in range(1, len(line) + 1):
                for word_begin in range(word_end):
                    word = line[word_begin:word_end]
                    if word in probs.keys() or len(word) == 1:
                        prob = unk_prob / vocab_num + probs[word]
                        score = best_score[word_begin] - math.log2(prob)
                        if score < best_score[word_end]:
                            best_score[word_end] = score
                            best_edge[word_end] = (word_begin, word_end)

            # 後ろ向きステップ
            words = []
            next_edge = best_edge[-1]
            while next_edge:
                word = line[next_edge[0]:next_edge[1]]
                words.append(word)
                next_edge = best_edge[next_edge[0]]
            words.reverse()
            words.append('\n')
            f.write(' '.join(words))
        # print(' '.join(words))
    print(f'<{output_file}>にテスト結果を書き込みました')


if __name__ == '__main__':
    args = arguments_parse()

    test_file = args.input if args.input else '..\..\data\wiki-ja-test.txt'
    train_file = args.train if args.train else '..\..\data\wiki-ja-train.word'
    # if args.input:
    #     test_file = args.input
    # else:
    #     test_file = '..\..\data\wiki-ja-test.txt'

    if args.train:
        train_file = args.train
    else:
        train_file = '..\..\data\wiki-ja-train.word'

    split_words(test_file, train_file)


'''
script/gradews.pl data/wiki-ja-test.word my_answer.word
-----
Sent Accuracy: 0.00% (/84)
Word Prec: 68.96% (1864/2703)
Word Rec: 80.80% (1864/2307)
F-meas: 74.41%
Bound Accuracy: 83.26% (2686/3226)
'''