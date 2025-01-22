setwd("/net/dali/home/chikina/yuehua/causalNonlinear/sergio/Methods")
library(kpcalg)
library(pcalg)
library(optparse)

option_list = list(
  make_option(c('-i', '--inputPATH'), action="store", type="character",
              help="input: data file location, samples (rows) x variables (cols), must be tab-separated w/ row names"),
  make_option(c('-o', '--outputPATH'), action="store", type="character",
              help="output: adjacency matrix file location"),
  make_option(c("--time_path"), action="store", type="character",
              help="output time file"),
  make_option(c("--alpha"), action="store", type="double",
               help="alpha in pc algorithm"),
  make_option(c("--zscore"), action="store", type="logical", default=FALSE,
              help = "z-score input data (i.e. set mean = 0, stdev = 1)")
)

opt = parse_args(OptionParser(option_list=option_list))

inputFile = opt$inputPATH
outputFile = opt$outputPATH
alpha = opt$alpha
relax = opt$relax
zscore = opt$zscore
timefile = opt$time_path
print(inputFile)
print(outputFile)
print(alpha)
print(zscore)
print(timefile)

data = read.table(inputFile, header = T, row.names = 1)

# scale data per volumn (variable)
if(zscore==TRUE) {
  # 1=rows 2=colums
  print("zscored")
  scale = function(x, margin=1){
          s = apply(x, margin, sd)
          m = apply(x, margin, mean)
          x = sweep(x, margin, m)
          x = sweep(x, margin, s, "/")
          x
  }
  data = scale(data, margin=2)
}

data = as.matrix(data)

# get start time
ptm <- proc.time()

# sufficient stat for PC
suffStat = list(C = cor(data), n = nrow(data))

# run PC
pc.fit = pc(suffStat,
            indepTest = gaussCItest,
            labels = colnames(data),
            alpha = alpha)

# PC results as adjacency matrix
pcres = summary(object = pc.fit)

# save adjacency matrix as output
write.table(pcres, file = outputFile, quote = F, row.names = T, col.names = T, sep = "\t")
# save runtime
write.table(proc.time() - ptm, file = timefile, col.names = F, quote=F)