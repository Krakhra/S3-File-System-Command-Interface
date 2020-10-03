ASSUMPTIONS:
1. for upload command, I assumed that the path is going to include the bucket and root. For example it has to be something like 
s3:/bucketname/folder1/folder2. A complete command would look like: upload textfile.txt s3:/bucketname/folder1/folder1a/

2. for s3 object names if total pathname is not supplied then I assume to look for the object in current directory. Arguments like
/folder/file.txt will not work, but cp s3:/bucket1/folder1/file.txt s3:/bucket2/folder1/ will work :)
