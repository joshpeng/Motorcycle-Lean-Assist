#!/usr/bin/env sh
#
# This script downloads the model weights and solver state for MLA.


URL='https://www.dropbox.com/s/6dvxifv4bn4ipso/aws_class_mcaug_model_iter_9000.caffemodel?dl=1'
URL2='https://www.dropbox.com/s/kldfmhb2loycsn4/aws_class_mcaug_model_iter_9000.solverstate?dl=1'
  
echo "Downloading model weights..."

wget $URL -O 'aws_class_mcaug_model_iter_9000.caffemodel'
  
echo "Downloading solver state..."

wget $URL2 -O 'aws_class_mcaug_model_iter_9000.solverstate'

echo "Done."