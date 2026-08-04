"# crawldata_manga" 
1. creat dataset forder
2. Each manga website has a different HTML structure, so each one requires a different crawling approach.
3. can custom file to get chapter you want 
 
* use label studio to annotate 
"C:\Users\dbinh\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\label-studio.exe" start
http://localhost:8080/
form :
<View>
  <Image name="image" value="$image"/>

  <RectangleLabels name="label" toName="image">
    <Label value="text" background="green"/>
  </RectangleLabels>
</View>

