getTP = function(estimate, truth) {
    estimate[estimate!=0] = 1
    truth[truth!=0] = 1
    TP = estimate * truth
    sum(TP)
}

getAdjTP = function(estimate, truth) {
    estimate[estimate!=0] = 1
    truth[truth!=0] = 1
    truth[t(truth)!=0] = 1
    TP = estimate * truth
    sum(TP)
}

getFP = function(estimate, truth) {
    estimate[estimate!=0] = 1
    tmp = truth
    tmp[truth!=0] = 0
    tmp[truth==0] = 1
    FP = estimate * tmp
    sum(FP)
}

getAdjFP = function(estimate, truth) {
    estimate[estimate!=0] = 1
    truth[truth!=0] = 1
    truth[t(truth)!=0] = 1
    tmp = truth
    tmp[truth!=0] = 0
    tmp[truth==0] = 1
    FP = estimate * tmp
    sum(FP)
}

getFN = function(estimate, truth) {
    truth[truth!=0] = 1
    tmp = estimate
    tmp[estimate!=0] = 0
    tmp[estimate==0] = 1
    FN = truth * tmp
    sum(FN)
}

getAdjFN = function(estimate, truth) {
    truth[truth!=0] = 1
    estimate[estimate!=0] = 1
    estimate[t(estimate)!=0] = 1
    tmp = estimate
    tmp[estimate!=0] = 0
    tmp[estimate==0] = 1
    FN = truth * tmp
    sum(FN)
}

getTN = function(estimate, truth) {
    tmp1 = estimate
    tmp2 = truth

    tmp1[estimate!=0] = 0
    tmp1[estimate==0] = 1

    tmp2[truth!=0] = 0
    tmp2[truth==0] = 1

    TN = tmp1 * tmp2
    sum(TN)
}

getPrecision = function(estimate, truth) {
    TP=getTP(estimate, truth)
    FP=getFP(estimate, truth)
    FN=getFN(estimate, truth)
    precision=TP*1.0/(TP+FP)
    precision*100
}

getRecall = function(estimate, truth) {
    TP=getTP(estimate, truth)
    FP=getFP(estimate, truth)
    FN=getFN(estimate, truth)
    recall=TP*1.0/(TP+FN)
    recall*100
}

getAdjPrecision = function(estimate, truth) {
    TP=getAdjTP(estimate, truth)
    FP=getAdjFP(estimate, truth)
    FN=getAdjFN(estimate, truth)
    precision=TP*1.0/(TP+FP)
    precision*100
}

getAdjRecall = function(estimate, truth) {
    TP=getAdjTP(estimate, truth)
    FP=getAdjFP(estimate, truth)
    FN=getAdjFN(estimate, truth)
    recall=TP*1.0/(TP+FN)
    recall*100
}

getOrientAccuracy = function(estimate, truth) {
    OrientTP = getTP(estimate, truth)
    AdjTP = getAdjTP(estimate, truth)
    accuracy = 0
    if (AdjTP != 0) {
        accuracy=OrientTP/AdjTP
    }
    accuracy*100
}

library(MESS)
precision_recall = function(estimate, truth, topE=30)  {
    estimate=as.matrix(estimate)
    truth=as.matrix(truth)
    sorted = sort(abs(estimate), decreasing = T)
    precision=c()
    recall=c()
    for(i in 1:topE) {
        cutoff = sorted[i]
        estimate[abs(estimate)<cutoff]=0
        TP=getTP(estimate, truth)
        FP=getFP(estimate, truth)
        FN=getFN(estimate, truth)
        precision=c(precision, TP*1.0/(TP+FP))
        recall=c(recall, TP*1.0/(TP+FN))
    }
    auc=auc(recall, precision, type = "spline")
    res = list("auprc"=auc, "precision"=precision, "recall"=recall)
    res
}

myShd = function (m1, m2) {
    m1 = as.matrix(m1)
    m2 = as.matrix(m2)
    m1[m1 != 0] <- 1
    m2[m2 != 0] <- 1
    shd <- 0
    s1 <- m1 + t(m1)
    s2 <- m2 + t(m2)
    s1[s1 == 2] <- 1
    s2[s2 == 2] <- 1
    ds <- s1 - s2
    ind <- which(ds > 0)
    m1[ind] <- 0
    shd <- shd + length(ind)/2
    ind <- which(ds < 0)
    m1[ind] <- m2[ind]
    shd <- shd + length(ind)/2
    d <- abs(m1 - m2)
    shd + sum((d + t(d)) > 0)/2
}


myShd2 = function (m1, m2) {
    m1 = as.matrix(m1)
    m2 = as.matrix(m2)
    m1[m1 != 0] <- 1
    m2[m2 != 0] <- 1
    m = m1 - m2
    m[m!=0] = 1
    sum(m)
}


