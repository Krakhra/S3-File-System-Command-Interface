ASSUMPTIONS:
1. for upload command, I assumed that the path is going to include the bucket and root. For example it has to be something like 
s3:/bucketname/folder1/folder2. A complete command would look like: upload textfile.txt s3:/bucketname/folder1/folder1a/

2. for s3 object names if total pathname is not supplied then I assume to look for the object in current directory. Arguments like
/folder/file.txt will not work, but cp s3:/bucket1/folder1/file.txt s3:/bucket2/folder1/ will work :)

3. for commands like cp and mv, inorder to move a object to current directory you have to use a '.' character example.
s3:/bucket/test/testfile.txt . (my extra feature)

4. For the files types in ls -l I simplified it to only show folder and file extension. I was not sure what exactly was wanted :( 

5. For upload, I assumed that if a total path is not present there will only be 2 arguments. Ex(upload <filename>)
things to fix so far, ls -l for buckets
