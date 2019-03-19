import tensorflow as tf
import time,os
import numpy as np
os.environ["CUDA_VISIBLE_DEVICES"] ="0"
#環境：python=3.x ,Tensorflow-gpu=1.9

model_tf_custom="../model_tf_custom/tf_line_model.ckpt"
model_tf_highAPI="../model_tf_highAPI/2tf_line_model.ckpt"

# 学習データと教師データを読み込み
x_train = np.loadtxt('../data/data_train.txt')
y_train = np.loadtxt('../data/data_teacher.txt')

#tensorflowの# 従来の APIを利用して開発した、特徴は、計算プロセスは明確的に見えます。
def train_custom():
    # W,bの変数を定義
    W = tf.Variable([0.5], dtype=tf.float32)
    b = tf.Variable([0.5], dtype=tf.float32)

    # x,yの入力データの変数を定義
    x = tf.placeholder(tf.float32) #学習データ
    y = tf.placeholder(tf.float32) #教師データ

    # 線形モデル定義
    linear_model = W * x + b

    # 損失関定義
    loss = tf.reduce_sum(tf.square(linear_model - y))
    # 学習率
    optimizer = tf.train.GradientDescentOptimizer(0.001)
    #最適化方式（小さい方式）
    train = optimizer.minimize(loss)

    # Session を定義、
    sess = tf.Session(config=tf.ConfigProto(
        allow_soft_placement=True, log_device_placement=False))

    # 計算グラフィックを初期化
    init = tf.global_variables_initializer()
    sess.run(init)

    # 100000回で学習させ
    start = time.time()
    for i in range(7000):

        sess.run(train, {x: x_train, y: y_train})
        if i%1000==0:
            print("step:%s"%i, sess.run(loss,{x: x_train, y: y_train}))
    print('train time: %.5f' % (time.time()-start))

    # Sessionごとを保存
    saver = tf.train.Saver()
    saver.save(sess, model_tf_custom)
    print(model_tf_custom)
    # 学習結果を確認
    print('weight: %s bias: %s loss: %s' % (sess.run(W), sess.run(b), sess.run(loss,{x: x_train, y: y_train})))

#tensorflowの高級 APIを利用して開発した、特徴は、学習と推論はより簡単になった、それらの処理はtensorflow内部側やってくれます。
#この例は開発中、推論の部分は未完成です。
def train_high_API():
    def model_fn(features, labels, mode):
        # 計算式
        W = tf.get_variable("W", [1], dtype=tf.float64)
        b = tf.get_variable("b", [1], dtype=tf.float64)
        y = W * features['x'] + b
        # 构建损失模型
        loss = tf.reduce_sum(tf.square(y - labels))
        # 学習子グラフィック
        global_step = tf.train.get_global_step()
        optimizer = tf.train.GradientDescentOptimizer(0.01)
        train = tf.group(optimizer.minimize(loss),
                         tf.assign_add(global_step, 1))
        # EstimatorSpecをと通じて学習
        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions=y,
            loss=loss,
            train_op=train
            )

    def train():
        # 学習などの設定
        estimator = tf.estimator.Estimator(model_fn=model_fn,model_dir=model_tf_highAPI)

        x_eavl = np.array([2., 5., 7., 9.])
        y_eavl = np.array([7.6, 17.2, 23.6, 28.8])

        train_input_fn = tf.estimator.inputs.numpy_input_fn(
            {"x": x_train}, y_train, batch_size=2, num_epochs=None, shuffle=True)
        estimator.train(input_fn=train_input_fn, steps=1000)

        train_input_fn_2 = tf.estimator.inputs.numpy_input_fn(
            {"x": x_train}, y_train, batch_size=2, num_epochs=1000, shuffle=False)

        eval_input_fn = tf.estimator.inputs.numpy_input_fn(
            {"x": x_eavl}, y_eavl, batch_size=2, num_epochs=1000, shuffle=False)


        train_metrics = estimator.evaluate(input_fn=train_input_fn_2)
        print("train metrics: %r" % train_metrics)

        eval_metrics = estimator.evaluate(input_fn=eval_input_fn)
        print("eval metrics: %s" % eval_metrics)
    estimator1 = tf.estimator.Estimator(model_fn=model_fn,model_dir=model_tf_highAPI)
    print(estimator1)

if __name__ == "__main__":
    #train_high_API()
    train_custom()