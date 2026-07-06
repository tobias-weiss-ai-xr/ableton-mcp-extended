{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 				{
			"major" : 8,
			"minor" : 5,
			"revision" : 6
		}
		,
		"classnamespace" : "box",
		"rect" : [ 0, 0, 800, 500 ],
		"bglocked" : 0,
		"openinpresentation" : 0,
		"default_fontsize" : 12.0,
		"default_fontface" : 0,
		"default_fontname" : "Arial",
		"gridonopen" : 1,
		"gridsize" : [ 15, 15 ],
		"gridsnaponopen" : 1,
		"objectsnaponopen" : 1,
		"statusbarvisible" : 2,
		"toolbarvisible" : 1,
		"lefttoolbarvisible" : 1,
		"handlevisibility" : 0,
		"description": "AbletonMCP Max Bridge — OSC relay for ableton-mcp-extended",
		"boxes" : [ 			{
				"box" : 					{
						"id" : "obj-1",
						"maxclass" : "newobj",
						"numinlets" : 1,
						"numoutlets" : 1,
						"outlettype" : [ "" ],
						"patching_rect" : [ 30, 40, 130, 22 ],
						"text" : "udpreceive 9000",
						"fontname" : "Arial",
						"fontsize" : 12.0,
						"fontface" : 0
					}

			}
			,
			{
				"box" : 					{
						"id" : "obj-2",
						"maxclass" : "newobj",
						"numinlets" : 1,
						"numoutlets" : 1,
						"outlettype" : [ "" ],
						"patching_rect" : [ 30, 80, 130, 22 ],
						"text" : "route /max",
						"fontname" : "Arial",
						"fontsize" : 12.0,
						"fontface" : 0
					}

			}
			,
			{
				"box" : 					{
						"id" : "obj-3",
						"maxclass" : "newobj",
						"numinlets" : 1,
						"numoutlets" : 6,
						"outlettype" : [ "", "", "", "", "", "" ],
						"patching_rect" : [ 30, 120, 250, 22 ],
						"text" : "select ping device/load device/info device/message bang open",
						"fontname" : "Arial",
						"fontsize" : 12.0,
						"fontface" : 0
					}

			}
			,
			{
				"box" : 					{
						"id" : "obj-4",
						"maxclass" : "newobj",
						"numinlets" : 1,
						"numoutlets" : 1,
						"outlettype" : [ "" ],
						"patching_rect" : [ 30, 170, 60, 22 ],
						"text" : "print bridge",
						"fontname" : "Arial",
						"fontsize" : 12.0,
						"fontface" : 0
					}

			}
			,
			{
				"box" : 					{
						"id" : "obj-5",
						"maxclass" : "newobj",
						"numinlets" : 1,
						"numoutlets" : 0,
						"outlettype" : [  ],
						"patching_rect" : [ 30, 210, 120, 22 ],
						"text" : "print bridge-ping",
						"fontname" : "Arial",
						"fontsize" : 12.0,
						"fontface" : 0
					}

			}
			,
			{
				"box" : 					{
						"id" : "obj-6",
						"maxclass" : "newobj",
						"numinlets" : 1,
						"numoutlets" : 1,
						"outlettype" : [ "" ],
						"patching_rect" : [ 30, 250, 130, 22 ],
						"text" : "print bridge-message",
						"fontname" : "Arial",
						"fontsize" : 12.0,
						"fontface" : 0
					}

			}
			,
			{
				"box" : 					{
						"id" : "obj-7",
						"maxclass" : "newobj",
						"numinlets" : 1,
						"numoutlets" : 1,
						"outlettype" : [ "" ],
						"patching_rect" : [ 30, 350, 400, 22 ],
						"text" : "comment AbletonMCP Max Bridge — Listening on port 9000",
						"fontname" : "Arial",
						"fontsize" : 12.0,
						"fontface" : 0
					}

			}
			,
			{
				"box" : 					{
						"id" : "obj-8",
						"maxclass" : "newobj",
						"numinlets" : 1,
						"numoutlets" : 1,
						"outlettype" : [ "" ],
						"patching_rect" : [ 30, 380, 480, 22 ],
						"text" : "comment OSC > udpreceive 9000 > route /max > select ... > print / send",
						"fontname" : "Arial",
						"fontsize" : 12.0,
						"fontface" : 0
					}

			}
			,
			{
				"box" : 					{
						"id" : "obj-9",
						"maxclass" : "newobj",
						"numinlets" : 1,
						"numoutlets" : 1,
						"outlettype" : [ "" ],
						"patching_rect" : [ 30, 290, 130, 22 ],
						"text" : "print bridge-bang",
						"fontname" : "Arial",
						"fontsize" : 12.0,
						"fontface" : 0
					}

			}
			,
			{
				"box" : 					{
						"id" : "obj-10",
						"maxclass" : "newobj",
						"numinlets" : 1,
						"numoutlets" : 1,
						"outlettype" : [ "" ],
						"patching_rect" : [ 30, 420, 480, 22 ],
						"text" : "comment Extend: connect select outlets to send objects for target devices",
						"fontname" : "Arial",
						"fontsize" : 12.0,
						"fontface" : 0
					}

			}
,
			{
				"box" : 					{
						"id" : "obj-11",
						"maxclass" : "newobj",
						"numinlets" : 1,
						"numoutlets" : 1,
						"outlettype" : [ "" ],
						"patching_rect" : [ 30, 460, 480, 22 ],
						"text" : "comment e.g., [send bridge-signal] → target device [receive bridge-signal]",
						"fontname" : "Arial",
						"fontsize" : 12.0,
						"fontface" : 0
					}

			}

		]
,
		"lines" : [ 			{
				"patchline" : 				{
					"source" : [ "obj-1", 0 ],
					"destination" : [ "obj-2", 0 ],
					"order" : 0
				}

			}
,
			{
				"patchline" : 				{
					"source" : [ "obj-2", 0 ],
					"destination" : [ "obj-3", 0 ],
					"order" : 0
				}

			}
,
			{
				"patchline" : 				{
					"source" : [ "obj-3", 4 ],
					"destination" : [ "obj-4", 0 ],
					"order" : 0
				}

			}
,
			{
				"patchline" : 				{
					"source" : [ "obj-3", 0 ],
					"destination" : [ "obj-5", 0 ],
					"order" : 0
				}

			}
,
			{
				"patchline" : 				{
					"source" : [ "obj-3", 3 ],
					"destination" : [ "obj-6", 0 ],
					"order" : 0
				}

			}
,
			{
				"patchline" : 				{
					"source" : [ "obj-3", 4 ],
					"destination" : [ "obj-9", 0 ],
					"order" : 0
				}

			}

		]
,
		"autosave" : 0

	}

}
