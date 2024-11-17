// After Effects Script: Apply Mosaic Masks from User-selected JSON

{
    // 手動でJSONをパースする関数（古い環境向け）
    function parseJSON(jsonString) {
        try {
            return eval('(' + jsonString + ')'); // 古い環境向けに eval を使用
        } catch (e) {
            alert("Error parsing JSON: " + e.message);
            return null;
        }
    }

    // ユーザーにJSONファイルを選択させる
    function getUserSelectedJSONPath() {
        var jsonFile = File.openDialog("Select a JSON file with mask data", "*.json");
        if (jsonFile) {
            jsonFile.open("r");
            var jsonData = jsonFile.read();
            jsonFile.close();
            return parseJSON(jsonData);
        } else {
            alert("No file selected. Script will terminate.");
            return null;
        }
    }

    // 動画の情報を取得してコンポジションを作成
    function createCompositionFromVideo(videoPath) {
        var videoFile = new File(videoPath);
        if (!videoFile.exists) {
            alert("Video file not found: " + videoPath);
            return null;
        }

        // 動画をインポート
        var importOptions = new ImportOptions(videoFile);
        var importedFile = app.project.importFile(importOptions);

        // 動画プロパティを取得
        var fps = importedFile.frameRate;
        var duration = importedFile.duration;
        var width = importedFile.width;
        var height = importedFile.height;

        // 新しいコンポジションを作成
        var comp = app.project.items.addComp("Mosaic Composition", width, height, 1, duration, fps);
        comp.layers.add(importedFile); // インポートした動画を追加
        return comp;
    }

    // Mosaicエフェクトを追加
    function addMosaicEffect(layer) {
        var mosaicEffect = layer.property("Effects").addProperty("ADBE Mosaic");
        mosaicEffect.property("水平ブロック").setValue(50); // 横ブロック数
        mosaicEffect.property("垂直ブロック").setValue(50);   // 縦ブロック数
        return mosaicEffect;
    }

    // マスクを適用
    function applyMasksToLayer(comp, jsonData) {
        function createMask(maskLayer, frame, vertices, frameDuration) {
            var time = frame * frameDuration;

            var maskShape = new Shape();
            if (!maskShape) {
                throw new Error("Shape オブジェクトの作成に失敗しました");
            }
            maskShape.vertices = vertices || [[0, 0]];
            maskShape.closed = true;

            var maskPath = maskLayer.property("Mask Path");
            if (!maskPath) {
                throw new Error("Mask Path プロパティが取得できません");
            }
            maskPath.setValueAtTime(time, maskShape);
        }
        var adjustmentLayer = comp.layers.addSolid([1, 1, 1], "Mosaic Adjustment", comp.width, comp.height, comp.pixelAspect, comp.duration);
        adjustmentLayer.adjustmentLayer = true;

        addMosaicEffect(adjustmentLayer);

        // 配列でマスクを管理する
        for (var maskIndex = 0; maskIndex < jsonData.masks.length; maskIndex++) {
            var mask = jsonData.masks[maskIndex];

            var maskLayer = adjustmentLayer.Masks.addProperty("Mask");
            if (!maskLayer) {
                throw new Error("マスクの追加に失敗しました");
            }
            maskLayer.maskMode = MaskMode.ADD;

            if (mask.begin_frame > 0) {
                createMask(maskLayer, mask.begin_frame - 1, null, comp.frameDuration);
            }

            // フレームごとのマスクデータを設定
            for (var i = mask.begin_frame; i <= mask.end_frame; i++) {
                var vertices = [];
                for (var k = 0; k < mask.vertices[i - mask.begin_frame].length; k++) {
                    var vertex = mask.vertices[i - mask.begin_frame][k];
                    vertices.push([vertex[0], vertex[1]]);
                }
                createMask(maskLayer, i, vertices, comp.frameDuration);
            }

            // 終了フレームの次のフレームのマスクを設定
            createMask(maskLayer, mask.end_frame + 1, null, comp.frameDuration);
        }

    }

    // メインスクリプト
    var jsonData = getUserSelectedJSONPath();
    if (jsonData) {
        app.beginUndoGroup("Apply Mosaic Masks");
        var comp = createCompositionFromVideo(jsonData.videoPath);
        comp.openInViewer();
        if (comp) {
            applyMasksToLayer(comp, jsonData);
        }
        app.endUndoGroup();
    }
}
